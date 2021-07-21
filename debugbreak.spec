Name:           debugbreak
Summary:        Break into the debugger programmatically
Version:        1.0
Release:        %autorelease

URL:            https://github.com/scottt/%{name}/
License:        BSD

Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make

# For testing:
BuildRequires:  gdb

# No compiled binaries are installed, so this would be empty.
%global debug_package %{nil}

%global common_description %{expand:
debugbreak.h allows you to put breakpoints in your C/C++ code with a call to
debug_break().

  • Include one header file and insert calls to debug_break() in the code where
    you wish to break into the debugger.
  • Supports GCC, Clang and MSVC.
  • Works well on ARM, AArch64, i686, x86-64, POWER and has a fallback code
    path for other architectures.
  • Works like the DebugBreak() function provided by Windows and QNX.}

%description %{common_description}


%package devel
Summary:        %{summary}

# Header-only library
Provides:       %{name}-static = %{version}-%{release}

%description devel %{common_description}


%prep
%autosetup


%build
%set_build_flags
%make_build -f GNUmakefile CFLAGS="${CFLAGS} -I." CXXFLAGS="${CXXFLAGS} -I."


%install
install -d '%{buildroot}%{_includedir}'
install -t '%{buildroot}%{_includedir}' -p -m 0644 %{name}.h

install -d '%{buildroot}%{_datadir}/%{name}'
install -t '%{buildroot}%{_datadir}/%{name}' -p -m 0644 %{name}-gdb.py


%check
# Each of the test files contains a programmatic breakpoint. We skip “trap”
# because it only tests __builtin_trap(), which is not provided by this library
# (and the test hangs on ppc64le anyway).
find test -type f -perm /0111 ! -name 'trap' |
  while read -r exe
  do
    # Script gdb to run the test file and record the backtrace.
    tee "${exe}-rpm-test.gdb" <<EOF
set pagination off
set logging file ${exe}-rpm-test.txt
set logging on
file ${exe}
run
bt
set logging off
quit
EOF
    gdb -q -x "${exe}-rpm-test.gdb" --batch </dev/null || :
    # Check that the program received SIGTRAP, trace/breakpoint trap
    grep -E 'SIG(TRAP|ILL)' "${exe}-rpm-test.txt"
  done

%files devel
%license COPYING
%doc HOW-TO-USE-DEBUGBREAK-GDB-PY.md
%doc README.md

%{_includedir}/%{name}.h

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/%{name}-gdb.py


%changelog
%autochangelog
