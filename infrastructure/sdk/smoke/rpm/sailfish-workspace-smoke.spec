Name: sailfish-workspace-smoke
Version: 0.1
Release: 1
Summary: Synthetic SDK cross-compilation probe
License: GPL-3.0-or-later

%description
Disposable synthetic test of SDK cross-compilation and RPM packaging.

%build
cat > hello.c <<'EOF'
#include <stdio.h>
int main(void) { puts("synthetic-sdk-build-ok"); return 0; }
EOF
gcc %{optflags} hello.c -o sailfish-workspace-smoke

%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 sailfish-workspace-smoke %{buildroot}%{_bindir}/sailfish-workspace-smoke

%files
%{_bindir}/sailfish-workspace-smoke
