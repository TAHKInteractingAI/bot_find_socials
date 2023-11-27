"""Extends setuptools to build macOS dmg or app blundle."""
from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
from pathlib import Path

from setuptools import Command

from cx_Freeze.common import normalize_to_list
from cx_Freeze.darwintools import (
    applyAdHocSignature,
    changeLoadReference,
    isMachOFile,
)
from cx_Freeze.exception import OptionError

__all__ = ["BdistDMG", "BdistMac"]


class BdistDMG(Command):
    """Create a Mac DMG disk image containing the Mac application bundle."""

    description = (
        "create a Mac DMG disk image containing the Mac application bundle"
    )
    user_options = [
        ("volume-label=", None, "Volume label of the DMG disk image"),
        (
            "applications-shortcut=",
            None,
            "Boolean for whether to include "
            "shortcut to Applications in the DMG disk image",
        ),
        ("silent", "s", "suppress all output except warnings"),
    ]

    def initialize_options(self):
        self.volume_label = self.distribution.get_fullname()
        self.applications_shortcut = False
        self.silent = None

    def finalize_options(self):
        if self.silent is None:
            self.silent = False

    def build_dmg(self):
        # Remove DMG if it already exists
        if os.path.exists(self.dmg_name):
            os.unlink(self.dmg_name)

        # Make dist folder
        self.dist_dir = os.path.join(self.build_dir, "dist")
        if os.path.exists(self.dist_dir):
            shutil.rmtree(self.dist_dir)
        self.mkpath(self.dist_dir)

        # Copy App Bundle
        dest_dir = os.path.join(
            self.dist_dir, os.path.basename(self.bundle_dir)
        )
        if self.silent:
            shutil.copytree(self.bundle_dir, dest_dir, symlinks=True)
        else:
            self.copy_tree(self.bundle_dir, dest_dir, preserve_symlinks=True)

        createargs = [
            "hdiutil",
            "create",
        ]
        if self.silent:
            createargs += ["-quiet"]
        createargs += [
            "-fs",
            "HFSX",
            "-format",
            "UDZO",
            self.dmg_name,
            "-imagekey",
            "zlib-level=9",
            "-srcfolder",
            self.dist_dir,
            "-volname",
            self.volume_label,
        ]

        if self.applications_shortcut:
            apps_folder_link = os.path.join(self.dist_dir, "Applications")
            os.symlink(
                "/Applications", apps_folder_link, target_is_directory=True
            )

        # Create the dmg
        if subprocess.call(createargs) != 0:
            raise OSError("creation of the dmg failed")

    def run(self):
        # Create the application bundle
        self.run_command("bdist_mac")

        # Find the location of the application bundle and the build dir
        self.bundle_dir = self.get_finalized_command("bdist_mac").bundle_dir
        self.build_dir = self.get_finalized_command("build_exe").build_base

        # Set the file name of the DMG to be built
        self.dmg_name = os.path.join(
            self.build_dir, self.volume_label + ".dmg"
        )

        self.execute(self.build_dmg, ())


class BdistMac(Command):
    """Create a Mac application bundle."""

    description = "create a Mac application bundle"

    plist_items: list[tuple[str, str]]
    include_frameworks: list[str]
    include_resources: list[str]

    user_options = [
        ("iconfile=", None, "Path to an icns icon file for the application."),
        (
            "qt-menu-nib=",
            None,
            "Location of qt_menu.nib folder for Qt "
            "applications. Will be auto-detected by default.",
        ),
        (
            "bundle-name=",
            None,
            "File name for the bundle application "
            "without the .app extension.",
        ),
        (
            "plist-items=",
            None,
            "A list of key-value pairs (type: list[tuple[str, str]]) to "
            "be added to the app bundle Info.plist file.",
        ),
        (
            "custom-info-plist=",
            None,
            "File to be used as the Info.plist in "
            "the app bundle. A basic one will be generated by default.",
        ),
        (
            "include-frameworks=",
            None,
            "A comma separated list of Framework "
            "directories to include in the app bundle.",
        ),
        (
            "include-resources=",
            None,
            "A list of tuples of additional "
            "files to include in the app bundle's resources directory, with "
            "the first element being the source, and second the destination "
            "file or directory name.",
        ),
        (
            "codesign-identity=",
            None,
            "The identity of the key to be used to sign the app bundle.",
        ),
        (
            "codesign-entitlements=",
            None,
            "The path to an entitlements file "
            "to use for your application's code signature.",
        ),
        (
            "codesign-deep=",
            None,
            "Boolean for whether to codesign using the --deep option.",
        ),
        (
            "codesign-timestamp",
            None,
            "Boolean for whether to codesign using the --timestamp option.",
        ),
        (
            "codesign-resource-rules",
            None,
            "Plist file to be passed to "
            "codesign's --resource-rules option.",
        ),
        (
            "absolute-reference-path=",
            None,
            "Path to use for all referenced "
            "libraries instead of @executable_path.",
        ),
        (
            "codesign-verify",
            None,
            "Boolean to verify codesign of the .app bundle using the codesign "
            "command",
        ),
        (
            "spctl-assess",
            None,
            "Boolean to verify codesign of the .app bundle using the spctl "
            "command",
        ),
        (
            "codesign-strict=",
            None,
            "Boolean for whether to codesign using the --strict option.",
        ),
        (
            "codesign-options=",
            None,
            "Option flags to be embedded in the code signature",
        ),
    ]

    def initialize_options(self):
        self.list_options = [
            "plist_items",
            "include_frameworks",
            "include_resources",
        ]
        for option in self.list_options:
            setattr(self, option, [])

        self.absolute_reference_path = None
        self.bundle_name = self.distribution.get_fullname()
        self.codesign_deep = None
        self.codesign_entitlements = None
        self.codesign_identity = None
        self.codesign_timestamp = None
        self.codesign_strict = None
        self.codesign_options = None
        self.codesign_resource_rules = None
        self.codesign_verify = None
        self.spctl_assess = None
        self.custom_info_plist = None
        self.iconfile = None
        self.qt_menu_nib = False

        self.build_base = None
        self.build_dir = None

    def finalize_options(self):
        # Make sure all options of multiple values are lists
        for option in self.list_options:
            setattr(self, option, normalize_to_list(getattr(self, option)))
        for item in self.plist_items:
            if not isinstance(item, tuple) or len(item) != 2:
                raise OptionError(
                    "Error, plist_items must be a list of key, value pairs "
                    "(list[tuple[str, str]]) (bad list item)."
                )

        # Define the paths within the application bundle
        self.set_undefined_options(
            "build_exe",
            ("build_base", "build_base"),
            ("build_exe", "build_dir"),
        )
        self.bundle_dir = os.path.join(
            self.build_base, f"{self.bundle_name}.app"
        )
        self.contents_dir = os.path.join(self.bundle_dir, "Contents")
        self.bin_dir = os.path.join(self.contents_dir, "MacOS")
        self.frameworks_dir = os.path.join(self.contents_dir, "Frameworks")
        self.resources_dir = os.path.join(self.contents_dir, "Resources")

    def create_plist(self):
        """Create the Contents/Info.plist file."""
        # Use custom plist if supplied, otherwise create a simple default.
        if self.custom_info_plist:
            with open(self.custom_info_plist, "rb") as file:
                contents = plistlib.load(file)
        else:
            contents = {
                "CFBundleIconFile": "icon.icns",
                "CFBundleDevelopmentRegion": "English",
                "CFBundleIdentifier": self.bundle_name,
                # Specify that bundle is an application bundle
                "CFBundlePackageType": "APPL",
                # Cause application to run in high-resolution mode by default
                # (Without this, applications run from application bundle may
                # be pixelated)
                "NSHighResolutionCapable": "True",
            }

        # Ensure CFBundleExecutable is set correctly
        contents["CFBundleExecutable"] = self.bundle_executable

        # add custom items to the plist file
        for key, value in self.plist_items:
            contents[key] = value

        with open(os.path.join(self.contents_dir, "Info.plist"), "wb") as file:
            plistlib.dump(contents, file)

    def set_absolute_reference_paths(self, path=None):
        """For all files in Contents/MacOS, set their linked library paths to
        be absolute paths using the given path instead of @executable_path.
        """
        if not path:
            path = self.absolute_reference_path

        files = os.listdir(self.bin_dir)

        for filename in files:
            filepath = os.path.join(self.bin_dir, filename)

            # Skip some file types
            if filepath[-1:] in ("txt", "zip") or os.path.isdir(filepath):
                continue

            out = subprocess.check_output(
                ("otool", "-L", filepath), encoding="utf_8"
            )
            for line in out.splitlines()[1:]:
                lib = line.lstrip("\t").split(" (compat")[0]

                if lib.startswith("@executable_path"):
                    replacement = lib.replace("@executable_path", path)

                    path, name = os.path.split(replacement)

                    # see if we provide the referenced file;
                    # if so, change the reference
                    if name in files:
                        changeLoadReference(filepath, lib, replacement)
            applyAdHocSignature(filepath)

    def find_qt_menu_nib(self):
        """Returns a location of a qt_menu.nib folder, or None if this is not
        a Qt application.
        """
        if self.qt_menu_nib:
            return self.qt_menu_nib
        if any(n.startswith("PyQt4.QtCore") for n in os.listdir(self.bin_dir)):
            name = "PyQt4"
        elif any(
            n.startswith("PySide.QtCore") for n in os.listdir(self.bin_dir)
        ):
            name = "PySide"
        else:
            return None

        qtcore = __import__(name, fromlist=["QtCore"]).QtCore
        libpath = str(
            qtcore.QLibraryInfo.location(qtcore.QLibraryInfo.LibrariesPath)
        )
        for subpath in [
            "QtGui.framework/Resources/qt_menu.nib",
            "Resources/qt_menu.nib",
        ]:
            path = os.path.join(libpath, subpath)
            if os.path.exists(path):
                return path

        # Last resort: fixed paths (macports)
        for path in [
            "/opt/local/Library/Frameworks/QtGui.framework/Versions/"
            "4/Resources/qt_menu.nib"
        ]:
            if os.path.exists(path):
                return path

        print("Could not find qt_menu.nib")
        raise OSError("Could not find qt_menu.nib")

    def prepare_qt_app(self):
        """Add resource files for a Qt application. Should do nothing if the
        application does not use QtCore.
        """
        nib_locn = self.find_qt_menu_nib()
        if nib_locn is None:
            return

        # Copy qt_menu.nib
        self.copy_tree(
            nib_locn, os.path.join(self.resources_dir, "qt_menu.nib")
        )

        # qt.conf needs to exist, but needn't have any content
        with open(os.path.join(self.resources_dir, "qt.conf"), "wb"):
            pass

    def run(self):
        self.run_command("build_exe")

        # Remove App if it already exists
        # ( avoids confusing issues where prior builds persist! )
        if os.path.exists(self.bundle_dir):
            shutil.rmtree(self.bundle_dir)
            print(f"Staging - Removed existing '{self.bundle_dir}'")

        # Find the executable name
        executable = self.distribution.executables[0].target_name
        _, self.bundle_executable = os.path.split(executable)
        print(f"Executable name: {self.build_dir}/{executable}")

        # Build the app directory structure
        self.mkpath(self.bin_dir)  # /MacOS
        self.mkpath(self.frameworks_dir)  # /Frameworks
        self.mkpath(self.resources_dir)  # /Resources

        # Copy the full build_exe to Contents/Resources
        self.copy_tree(self.build_dir, self.resources_dir)

        # Move only executables in Contents/Resources to Contents/MacOS
        for executable in self.distribution.executables:
            source = os.path.join(self.resources_dir, executable.target_name)
            target = os.path.join(self.bin_dir, executable.target_name)
            self.move_file(source, target)

        # Make symlink between Resources/lib and Contents/MacOS so we can use
        # none-relative reference paths in order to pass codesign...
        resources_lib_dir = os.path.join(self.resources_dir, "lib")
        origin = os.path.join(self.bin_dir, "lib")
        relative_reference = os.path.relpath(resources_lib_dir, self.bin_dir)
        self.execute(
            os.symlink,
            (relative_reference, origin, True),
            msg=f"linking {origin} -> {relative_reference}",
        )
        # Make symlink between Resources/share and Contents/MacOS too.
        resource_share_dir = os.path.join(self.resources_dir, "share")
        if os.path.exists(resource_share_dir):
            origin = os.path.join(self.bin_dir, "share")
            relative_reference = os.path.relpath(
                resource_share_dir, self.bin_dir
            )
            self.execute(
                os.symlink,
                (relative_reference, origin, True),
                msg=f"linking {origin} -> {relative_reference}",
            )

        # Copy the icon
        if self.iconfile:
            self.copy_file(
                self.iconfile, os.path.join(self.resources_dir, "icon.icns")
            )

        # Copy in Frameworks
        for framework in self.include_frameworks:
            self.copy_tree(
                framework,
                os.path.join(self.frameworks_dir, os.path.basename(framework)),
            )

        # Copy in Resources
        for resource, destination in self.include_resources:
            if os.path.isdir(resource):
                self.copy_tree(
                    resource, os.path.join(self.resources_dir, destination)
                )
            else:
                parent_dirs = os.path.dirname(
                    os.path.join(self.resources_dir, destination)
                )
                os.makedirs(parent_dirs, exist_ok=True)
                self.copy_file(
                    resource, os.path.join(self.resources_dir, destination)
                )

        # Create the Info.plist file
        self.execute(self.create_plist, ())

        # Make library references absolute if enabled
        if self.absolute_reference_path:
            self.execute(self.set_absolute_reference_paths, ())

        # For a Qt application, run some tweaks
        self.execute(self.prepare_qt_app, ())

        # Sign the app bundle if a key is specified
        self._codesign(self.bundle_dir)

    def _codesign(self, root_path):
        """Run codesign on all .so, .dylib and binary files in reverse order.
        Signing from inside-out.
        """
        if not self.codesign_identity:
            return

        print(f"About to sign: '{self.bundle_dir}'")
        binaries_to_sign = []

        # Identify all binary files
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                full_path = Path(os.path.join(dirpath, filename))

                if isMachOFile(full_path):
                    binaries_to_sign.append(full_path)

        # Sort files by depth, so we sign the deepest files first
        binaries_to_sign.sort(key=lambda x: str(x).count(os.sep), reverse=True)

        for binary_path in binaries_to_sign:
            self._codesign_file(binary_path, self._get_sign_args())

        self._verify_signature()
        print("Finished .app signing")

    def _get_sign_args(self):
        signargs = ["codesign", "--sign", self.codesign_identity, "--force"]

        if self.codesign_timestamp:
            signargs.append("--timestamp")

        if self.codesign_strict:
            signargs.append(f"--strict={self.codesign_strict}")

        if self.codesign_deep:
            signargs.append("--deep")

        if self.codesign_options:
            signargs.append("--options")
            signargs.append(self.codesign_options)

        if self.codesign_entitlements:
            signargs.append("--entitlements")
            signargs.append(self.codesign_entitlements)
        return signargs

    def _codesign_file(self, file_path, sign_args):
        print(f"Signing file: {file_path}")
        sign_args.append(file_path)
        subprocess.run(sign_args, check=False)

    def _verify_signature(self):
        if self.codesign_verify:
            verify_args = [
                "codesign",
                "-vvv",
                "--deep",
                "--strict",
                self.bundle_dir,
            ]
            print("Running codesign verification")
            result = subprocess.run(
                verify_args, capture_output=True, text=True, check=False
            )
            print("ExitCode:", result.returncode)
            print(" stdout:", result.stdout)
            print(" stderr:", result.stderr)

        if self.spctl_assess:
            spctl_args = [
                "spctl",
                "--assess",
                "--raw",
                "--verbose=10",
                "--type",
                "exec",
                self.bundle_dir,
            ]
            try:
                completed_process = subprocess.run(
                    spctl_args,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                print(
                    "spctl command's output: "
                    f"{completed_process.stdout.decode()}"
                )
            except subprocess.CalledProcessError as error:
                print(f"spctl check got an error: {error.stdout.decode()}")
                raise
