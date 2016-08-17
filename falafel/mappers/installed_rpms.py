import json
from collections import defaultdict
from distutils.version import LooseVersion

from falafel.core.plugins import mapper
from falafel.util import rsplit
from falafel.core import MapperOutput, computed

KNOWN_ARCHITECTURES = [
    'x86_64',
    'i386',
    'i486',
    'i586',
    'i686',
    'src',
    'ia64',
    'ppc',
    'ppc64',
    's390',
    's390x',
    'amd64',
    '(none)',
    'noarch'
]


@mapper('installed-rpms')
class InstalledRpms(MapperOutput):

    @computed
    def corrupt(self):
        return "__error" in self

    def get_max(self, name):
        """
        Returns the highest version of the installed RPM with the given name
        """
        return max(self[name]) if name in self else None

    @classmethod
    def parse_content(cls, content):
        packages = defaultdict(list)
        try:
            for line in content:
                if line.startswith("error:"):
                    packages["__error"] = True
                else:
                    rpm = json.loads(line)
                    packages[rpm["name"]].append(InstalledRpm(rpm))
        except:
            for line in content:
                if line.startswith("error:"):
                    packages["__error"] = True
                else:
                    if line.strip():
                        name, rpm = parse_line(line)
                        packages[name].append(InstalledRpm(rpm))
        return packages if packages else None


class InstalledRpm(MapperOutput):

    @computed
    def package(self):
        return "%s-%s-%s" % (
            self["name"],
            self["version"],
            self["release"]
        )

    def __str__(self):
        return self.package

    @classmethod
    def from_package(cls, package_string):
        return InstalledRpm(parse_package(package_string))

    def __eq__(self, other):
        return (
            self["name"] == other["name"] and
            LooseVersion(self["version"]) == LooseVersion(other["version"]) and
            LooseVersion(self["release"]) == LooseVersion(other["release"])
        )

    def __lt__(self, other):
        if self["name"] != other["name"]:
            raise ValueError("Cannot compare packages with differing names %s != %s" % (self["name"], other["name"]))

        if self == other:
            return False

        self_v = LooseVersion(self["version"])
        other_v = LooseVersion(other["version"])

        if self_v < other_v:
            return True
        elif self_v > other_v:
            return False
        else:
            return LooseVersion(self["release"]) < LooseVersion(other["release"])

    def __gt__(self, other):
        return other.__lt__(self)

    def __le__(self, other):
        return self == other or self.__lt__(other)

    def __ge__(self, other):
        return self == other or self.__gt__(other)


SOSREPORT_KEYS = [
    "installtime", "buildtime", "vendor",
    "buildserver", "pgpsig", "pgpsig-short"
]


def parse_package(package_string):
    pkg, arch = rsplit(package_string, ".")
    if arch not in KNOWN_ARCHITECTURES:
        pkg, arch = (package_string, None)
    pkg, release = rsplit(pkg, "-")
    name, version = rsplit(pkg, "-")
    return {
        "name": name,
        "version": version,
        "release": release,
        "arch": arch
    }


def parse_line(line):
    try:
        pkg, rest = line.split(None, 1)
    except ValueError:
        rpm = parse_package(line.strip())
        return rpm["name"], rpm
    rpm = parse_package(pkg)
    rest = rest.split("\t")
    for i, value in enumerate(rest):
        rpm[SOSREPORT_KEYS[i]] = value
    return rpm["name"], rpm
