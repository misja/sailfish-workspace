cmake_minimum_required(VERSION 3.18)
project(secrets_rnp_correction_fixture LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
find_package(Qt5 5.6 REQUIRED COMPONENTS Core)
find_package(PkgConfig REQUIRED)
pkg_check_modules(SAILFISH REQUIRED IMPORTED_TARGET sailfishsecrets sailfishcrypto
                  sailfishsecretspluginapi sailfishcryptopluginapi)
set(BACKEND "/home/ubuntu/pass-rnp-only-sdk-probe-20261101-r2/BUILD/pass-rnp-only-sdk-probe-0.18.1")
add_library(actual_rnp SHARED IMPORTED)
set_target_properties(actual_rnp PROPERTIES
    IMPORTED_LOCATION "${BACKEND}/_deps/rnp-build/src/lib/librnp.so.0.18.1"
    INTERFACE_INCLUDE_DIRECTORIES "${BACKEND}/rnp/include;${BACKEND}/_deps/rnp-build/src/lib")
set(COMMON source/rnp/rnp.cpp source/secrets/rnp/rnpffi.cpp source/secrets/rnp/rnpkeys.cpp)
# Actual module is built, never loaded into an existing daemon.
add_library(sailfishcrypto-rnp-corrected MODULE source/secrets/rnp/plugin.cpp ${COMMON})
target_compile_definitions(sailfishcrypto-rnp-corrected PRIVATE SAILFISHCRYPTO_TESTPLUGIN=1)
target_include_directories(sailfishcrypto-rnp-corrected PRIVATE source/rnp)
target_link_libraries(sailfishcrypto-rnp-corrected PRIVATE Qt5::Core PkgConfig::SAILFISH actual_rnp)
add_executable(secrets_rnp_probe probe.cpp ${COMMON})
target_compile_definitions(secrets_rnp_probe PRIVATE PLUGIN_CORRECTED=1)
target_include_directories(secrets_rnp_probe PRIVATE source/rnp source/secrets/rnp)
target_link_libraries(secrets_rnp_probe PRIVATE Qt5::Core PkgConfig::SAILFISH actual_rnp)
add_executable(secrets_rnp_pristine_probe probe.cpp
    pristine/rnp/rnp.cpp pristine/secrets/rnp/rnpffi.cpp pristine/secrets/rnp/rnpkeys.cpp)
target_compile_definitions(secrets_rnp_pristine_probe PRIVATE PLUGIN_CORRECTED=0)
target_include_directories(secrets_rnp_pristine_probe PRIVATE pristine/rnp pristine/secrets/rnp)
target_link_libraries(secrets_rnp_pristine_probe PRIVATE Qt5::Core PkgConfig::SAILFISH actual_rnp)

# Actual pinned upstream daemon; only main's plugin search path is fixture-bound.
find_package(Qt5 5.6 REQUIRED COMPONENTS DBus Concurrent Sql)
pkg_check_modules(DAEMON_SYSTEM REQUIRED IMPORTED_TARGET dbus-1 systemsettings)
set(DAEMON_SOURCES
    upstream/daemon/main.cpp upstream/daemon/controller.cpp upstream/daemon/plugin_p.cpp upstream/daemon/requestqueue.cpp
    upstream/daemon/SecretsImpl/metadatadb.cpp upstream/daemon/SecretsImpl/pluginfunctionwrappers.cpp
    upstream/daemon/SecretsImpl/pluginwrapper.cpp upstream/daemon/SecretsImpl/secrets.cpp
    upstream/daemon/SecretsImpl/secretsrequestprocessor.cpp upstream/daemon/SecretsImpl/applicationpermissions.cpp
    upstream/daemon/SecretsImpl/dataprotector.cpp upstream/daemon/SecretsImpl/secretscryptohelpers.cpp
    upstream/daemon/CryptoImpl/crypto.cpp upstream/daemon/CryptoImpl/cryptorequestprocessor.cpp
    upstream/daemon/CryptoImpl/cryptopluginfunctionwrappers.cpp upstream/daemon/CryptoImpl/cryptopluginwrapper.cpp
    upstream/database/database.cpp upstream/database/util.cpp)
file(GLOB DAEMON_HEADERS "upstream/daemon/*_p.h"
     "upstream/daemon/SecretsImpl/*_p.h" "upstream/daemon/CryptoImpl/*_p.h")
add_executable(secrets_rnp_fixture_daemon ${DAEMON_SOURCES} ${DAEMON_HEADERS})
target_include_directories(secrets_rnp_fixture_daemon PRIVATE
    upstream/lib upstream/daemon upstream/daemon/SecretsImpl upstream/daemon/CryptoImpl upstream/database)
target_link_libraries(secrets_rnp_fixture_daemon PRIVATE Qt5::Core Qt5::DBus Qt5::Concurrent Qt5::Sql
    PkgConfig::SAILFISH PkgConfig::DAEMON_SYSTEM)
add_executable(secrets_rnp_api_probe api-probe.cpp)
target_link_libraries(secrets_rnp_api_probe PRIVATE Qt5::Core Qt5::DBus PkgConfig::SAILFISH)
