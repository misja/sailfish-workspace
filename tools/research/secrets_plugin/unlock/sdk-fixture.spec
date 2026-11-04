Name: secrets-unlock-fixture
Version: 0.1
Release: 0
Summary: Protected key interaction through stock PasswordAgent
License: GPL-3.0-or-later AND MIT AND BSD-3-Clause AND (GPL-2.0-only OR GPL-3.0-only)
Source0: factory.tar.gz
Source1: qttotp.tar.gz
Source2: factory-seams.patch
Source3: qttotp-qt56.patch
Source4: CMakeLists.txt
Source5: SecretsPass.h
Source6: SecretsPass.cpp
Source7: probe.cpp
Source8: passwordagent.tar.gz
Source9: agent.cpp
ExclusiveArch: aarch64
BuildRequires: cmake >= 3.18
BuildRequires: libsailfishcrypto-devel = 0.2.44-1.14.2.jolla

%description
Fresh-build all selected generic factory sources against patched headers, actual
Sailfish Crypto and pinned QtTotp. No native RNP/GPG linkage, install or runtime.

%prep
%setup -q -c -T -n secrets-unlock-fixture-%{version}
mkdir factory qttotp passwordagent
tar -xzf %{SOURCE0} -C factory
tar -xzf %{SOURCE1} -C qttotp
git -C factory apply %{SOURCE2}
git -C qttotp apply %{SOURCE3}
cp %{SOURCE4} CMakeLists.txt
cp %{SOURCE5} SecretsPass.h
cp %{SOURCE6} SecretsPass.cpp
cp %{SOURCE7} probe.cpp
tar -xzf %{SOURCE8} -C passwordagent
cp %{SOURCE9} agent.cpp

%build
%cmake
cmake --build . --parallel 1 --verbose
readelf -h secrets_unlock_probe
readelf -d secrets_unlock_probe
readelf -h secrets_unlock_agent
readelf -h libsailfishsecrets-passwordagentauth-fixture.so
sha256sum secrets_unlock_probe secrets_unlock_agent libsailfishsecrets-passwordagentauth-fixture.so
