# Research only: fresh disposable rpmbuild -bc tree; no install or RPM creation.
%global _smp_mflags -j1
Name:           pass-rnp-only-sdk-probe
Version:        0.18.1
Release:        0
Summary:        Existing public backend RNP-only executable link probe
# Research metadata only; not a distribution license determination.
License:        BSD-2-Clause AND BSD-3-Clause AND Apache-2.0 AND MIT
URL:            https://github.com/shemeshg/gpgme-cmake-example
Source0:        gpgfactory-e53cd22c365ce170ebeaed70984207a8206d00eb.tar.gz
Source1:        rnp-aad1892e4d8423398a0b973bd0a7e4544c359afc.tar.gz
Source2:        sexpp-c641a2f36520bab783657a58650d9fda548b9dec.tar.gz
Source3:        corrections.patch
Source4:        rnp-only.patch
Source5:        sdk-CMakeLists.txt
Source6:        probe.cpp
ExclusiveArch:  aarch64
BuildRequires:  cmake >= 3.18
BuildRequires:  git-core = 2.50.1+git1-1.9.8.jolla
BuildRequires:  openssl-devel = 3.5.6+git1-1.14.1.jolla
BuildRequires:  json-c-devel = 0.18+git1-1.5.2.jolla
BuildRequires:  bzip2-devel = 1.0.8+git3-1.7.2.jolla
BuildRequires:  zlib-devel = 1.3.1+git1-1.9.2.jolla

%description
Disposable SDK executable compile/link probe of the existing public backend.
Applies the separately reviewed corrections and RNP-only research patches.
Uses pinned RNP and sexpp with the upstream OpenSSL helper, which builds AND RUNS.
Does not execute the public fixture, install libraries or create an RPM.

%prep
# Coordinator verifies all staged file hashes against local inputs before invocation.
%setup -q -c -T -n pass-rnp-only-sdk-probe-%{version}
mkdir factory rnp
tar -xzf %{SOURCE0} -C factory --strip-components=1
tar -xzf %{SOURCE1} -C rnp --strip-components=1
mkdir -p rnp/src/libsexpp
tar -xzf %{SOURCE2} -C rnp/src/libsexpp --strip-components=1
(cd factory && git apply --check %{SOURCE3} && git apply %{SOURCE3})
(cd factory && git apply --check %{SOURCE4} && git apply %{SOURCE4})
cp %{SOURCE5} CMakeLists.txt
cp %{SOURCE6} probe.cpp

%build
export CMAKE_BUILD_PARALLEL_LEVEL=1
%cmake --trace-source="$PWD/rnp/cmake/Modules/FindOpenSSLFeatures.cmake" \
    --trace-expand --trace-redirect="$PWD/sdk-openssl-feature-trace.log"
cmake --build . --target public_backend_probe --parallel 1 --verbose
readelf -h public_backend_probe
readelf -d public_backend_probe
sha256sum public_backend_probe
