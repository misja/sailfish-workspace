Name: secrets-pass-consumer-fixture
Version: 0.1
Release: 0
Summary: Synthetic pass entry consumer through Sailfish Crypto
License: GPL-3.0-or-later AND MIT AND (GPL-2.0-only OR GPL-3.0-only)
Source0: factory.tar.gz
Source1: qttotp.tar.gz
Source2: factory-seams.patch
Source3: qttotp-qt56.patch
Source4: CMakeLists.txt
Source5: SecretsPass.h
Source6: SecretsPass.cpp
Source7: probe.cpp
ExclusiveArch: aarch64
BuildRequires: cmake >= 3.18
BuildRequires: libsailfishcrypto-devel = 0.2.44-1.14.2.jolla

%description
Fresh-build all selected generic factory sources against patched headers, actual
Sailfish Crypto and pinned QtTotp. No native RNP/GPG linkage, install or runtime.

%prep
%setup -q -c -T -n secrets-pass-consumer-fixture-%{version}
mkdir factory qttotp
tar -xzf %{SOURCE0} -C factory
tar -xzf %{SOURCE1} -C qttotp
git -C factory apply %{SOURCE2}
git -C qttotp apply %{SOURCE3}
cp %{SOURCE4} CMakeLists.txt
cp %{SOURCE5} SecretsPass.h
cp %{SOURCE6} SecretsPass.cpp
cp %{SOURCE7} probe.cpp

%build
%cmake
cmake --build . --parallel 1 --verbose
readelf -h secrets_pass_consumer
readelf -d secrets_pass_consumer
sha256sum secrets_pass_consumer
