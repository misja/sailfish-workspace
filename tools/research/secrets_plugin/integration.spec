# Synthetic module/fixture build only; fresh SDK rpmbuild -bc scratch.
Name:           secrets-rnp-api-fixture
Version:        0.1
Release:        0
Summary:        Secrets RNP correction and regression fixtures
License:        BSD-3-Clause AND GPL-3.0-or-later
Source0:        corrected.tar.gz
Source1:        pristine.tar.gz
Source2:        CMakeLists.txt
Source3:        probe.cpp
Source4:        upstream.tar.gz
Source5:        daemon-fixture.patch
Source6:        api-probe.cpp
ExclusiveArch:  aarch64
BuildRequires:  cmake >= 3.18
BuildRequires:  libsailfishcrypto-devel = 0.2.44-1.14.2.jolla
BuildRequires:  libsailfishsecretspluginapi-devel = 0.2.44-1.14.2.jolla
BuildRequires:  libsailfishcryptopluginapi-devel = 0.2.44-1.14.2.jolla

%description
Builds module and direct-class fixtures with actual SDK interfaces and verified
retained RNP library. Coordinator verifies input/archive/library hashes.
No installation, package creation or runtime in this recipe.

%prep
%setup -q -c -T -n secrets-rnp-api-fixture-%{version}
mkdir source pristine
tar -xzf %{SOURCE0} -C source
tar -xzf %{SOURCE1} -C pristine
cp %{SOURCE2} CMakeLists.txt
cp %{SOURCE3} probe.cpp
mkdir upstream
tar -xzf %{SOURCE4} -C upstream
git -C upstream apply %{SOURCE5}
cp %{SOURCE6} api-probe.cpp

%build
%cmake
cmake --build . --parallel 1 --verbose
readelf -h secrets_rnp_probe
readelf -h libsailfishcrypto-rnp-corrected.so
sha256sum secrets_rnp_probe secrets_rnp_pristine_probe libsailfishcrypto-rnp-corrected.so

readelf -h secrets_rnp_fixture_daemon
readelf -h secrets_rnp_api_probe
sha256sum secrets_rnp_fixture_daemon secrets_rnp_api_probe
