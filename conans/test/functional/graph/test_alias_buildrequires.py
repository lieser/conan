import unittest

from conans.test.utils.tools import TestClient, GenConanfile


class AliasBuildRequiresTestCase(unittest.TestCase):

    def test_alias_buildrequires(self):
        # https://github.com/conan-io/conan/issues/8176
        t = TestClient()
        t.save({
            'libA.py': GenConanfile(),
            'libB.py': GenConanfile().with_requires("libA/[^7.1.0]"),
            'libC.py': GenConanfile().with_requires("libA/[^7.1.0]", "libB/[^4.2.0]"),
            'testFrameworkForC.py': GenConanfile()
                .with_requires("libA/7.1.0+alias", "libB/4.2.0+alias"),
            'libD.py': GenConanfile().with_requires("libA/[^7.1.0]", "libB/[^4.2.0]",
                                                    "libC/[^4.1.0]")
                .with_build_requirement("testFrameworkForC/conan", force_host_context=True),
            'app.py': GenConanfile().with_requires("libA/conan", "libB/conan", "libC/conan",
                                                   "libD/conan")
                .with_build_requirement("testFrameworkForC/conan", force_host_context=True),
        })
        # Let's create all the packages in order
        t.run('export libA.py libA/7.1.0@')
        t.run('export libA.py libA/conan@')

        t.run('export libB.py libB/4.2.0@')
        t.run('export libB.py libB/conan@')

        t.run('export libC.py libC/4.1.0@')
        t.run('export libC.py libC/conan@')

        t.run('alias libA/7.1.0+alias@ libA/conan@')
        t.run('alias libB/4.2.0+alias@ libB/conan@')
        t.run('export testFrameworkForC.py testFrameworkForC/conan@')

        t.run('export libD.py libD/conan@')
        t.run('info app.py --only requires')
        print(t.current_folder)
        print(t.out)

        t.run('create app.py app/version@ --build=missing')
        print(t.out)
