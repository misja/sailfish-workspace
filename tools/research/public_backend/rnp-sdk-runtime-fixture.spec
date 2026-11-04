# Research fixture build only: fresh rpmbuild -bc scratch tree.
Name:           rnp-sdk-runtime-fixture
Version:        0.1
Release:        0
Summary:        Synthetic public RNP-only backend runtime fixture
License:        GPL-3.0-or-later
Source0:        probe.cpp
Source1:        sdk-runtime-CMakeLists.txt
ExclusiveArch:  aarch64
BuildRequires:  cmake >= 3.18

%description
Builds only synthetic fixture executable against reviewed existing backend
artifacts. Coordinator verifies staged source and existing artifact hashes.
No vendor rebuild, package creation, installation or runtime in this recipe.

%prep
%setup -q -c -T -n rnp-sdk-runtime-fixture-%{version}
cp %{SOURCE0} probe.cpp
cp %{SOURCE1} CMakeLists.txt

%build
%cmake
cmake --build . --target public_backend_sdk_probe --parallel 1 --verbose
readelf -h public_backend_sdk_probe
readelf -d public_backend_sdk_probe
sha256sum public_backend_sdk_probe
