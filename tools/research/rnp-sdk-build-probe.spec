# Research only: invoke rpmbuild -bc with a fresh explicit _topdir.
# No install, package creation, stock-library replacement or device operation.
%global _smp_mflags -j1

Name:           rnp-sdk-build-probe
Version:        0.18.1
Release:        0
Summary:        Build-only pinned RNP OpenSSL feasibility probe
License:        BSD-2-Clause AND BSD-3-Clause AND Apache-2.0 AND MIT
URL:            https://github.com/rnpgp/rnp
Source0:        rnp-aad1892e4d8423398a0b973bd0a7e4544c359afc.tar.gz
Source1:        sexpp-c641a2f36520bab783657a58650d9fda548b9dec.tar.gz
ExclusiveArch:  aarch64
BuildRequires:  cmake >= 3.18
BuildRequires:  git-core = 2.50.1+git1-1.9.8.jolla
BuildRequires:  openssl-devel = 3.5.6+git1-1.14.1.jolla
BuildRequires:  json-c-devel = 0.18+git1-1.5.2.jolla
BuildRequires:  bzip2-devel = 1.0.8+git3-1.7.2.jolla
BuildRequires:  zlib-devel = 1.3.1+git1-1.9.2.jolla

%description
Disposable SDK build of upstream librnp using the maintained OpenSSL backend and
the exact bundled sexpp gitlink. Configuration builds AND RUNS the upstream
OpenSSL feature helper; authorization must explicitly cover that execution.
This is an engine feasibility probe, not the complete public backend or a package.

%prep
echo 'ca0f1b82ea0867c7b9ec62f29e70edc2b609cc591cf574d38a30e9947f21594d  %{SOURCE0}' | sha256sum -c -
echo '67ccd41f678d4b1e3daa434709f8810fc57c7405a907bd5e62ee505c8364c7de  %{SOURCE1}' | sha256sum -c -
%setup -q -c -T -n rnp-sdk-probe-%{version}
tar -xzf %{SOURCE0} --strip-components=1
mkdir -p src/libsexpp
tar -xzf %{SOURCE1} -C src/libsexpp --strip-components=1
test -f cmake/version.cmake
test -f src/libsexpp/cmake/version.cmake

%build
# The actual SDK macro is in-source: only this disposable RPM build copy changes.
# Limit also the upstream nested feature-helper build, which inherits the env.
export CMAKE_BUILD_PARALLEL_LEVEL=1
%cmake --trace-source="$PWD/cmake/Modules/FindOpenSSLFeatures.cmake" \
    --trace-expand --trace-redirect="$PWD/sdk-openssl-feature-trace.log" \
    -DCRYPTO_BACKEND=openssl \
    -DSYSTEM_LIBSEXPP=OFF \
    -DBUILD_TESTING=OFF -DDOWNLOAD_GTEST=OFF \
    -DENABLE_DOC=Off \
    -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
    -DFETCHCONTENT_UPDATES_DISCONNECTED=ON
cmake --build . --target librnp --parallel 1 --verbose
# Record build artifacts without running librnp or RNP command-line tools.
readelf -h fossl/build/findopensslfeatures
readelf -d fossl/build/findopensslfeatures
readelf -h src/lib/librnp.so
readelf -d src/lib/librnp.so
sha256sum fossl/build/findopensslfeatures src/lib/librnp.so
