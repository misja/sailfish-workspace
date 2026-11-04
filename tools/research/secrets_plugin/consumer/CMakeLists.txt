cmake_minimum_required(VERSION 3.18)
project(secrets_pass_consumer_fixture LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Qt5 5.6 REQUIRED COMPONENTS Core DBus)
find_package(PkgConfig REQUIRED)
pkg_check_modules(CRYPTO REQUIRED IMPORTED_TARGET sailfishcrypto)
find_package(Threads REQUIRED)
add_executable(secrets_pass_consumer
    SecretsPass.cpp probe.cpp
    factory/libpgpfactory/GpgIdManage.cpp
    factory/libpgpfactory/InterfacePassFile.cpp
    factory/libpgpfactory/InterfacePassHelper.cpp
    factory/libpgpfactory/FileSearch.cpp
    factory/libpgpfactory/uuid.cpp
    qttotp/totp.cpp qttotp/Base32.cpp qttotp/Clock.cpp)
target_include_directories(secrets_pass_consumer PRIVATE
    factory/libpgpfactory/export factory/libpgpfactory/RnpCore/export qttotp)
target_link_libraries(secrets_pass_consumer PRIVATE Qt5::Core Qt5::DBus PkgConfig::CRYPTO Threads::Threads)
