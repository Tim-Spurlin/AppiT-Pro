cmake_minimum_required(VERSION 3.20)
project(HAASP VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Qt6 components
find_package(Qt6 6.4 REQUIRED COMPONENTS Core Widgets Qml Quick QuickControls2 Concurrent)

# Find libgit2
find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBGIT2 REQUIRED libgit2)

# Find other dependencies
pkg_check_modules(PROTOBUF REQUIRED protobuf)
pkg_check_modules(GRPC REQUIRED grpc++)

# Qt6 automatic MOC, UIC, RCC
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/src)
include_directories(${PROTOBUF_INCLUDE_DIRS})
include_directories(${GRPC_INCLUDE_DIRS})
include_directories(${LIBGIT2_INCLUDE_DIRS})

# Compiler flags for performance optimization
if(CMAKE_BUILD_TYPE MATCHES Release)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -mavx2")
endif()

# Enable hidden QML optimizations
add_compile_definitions(QML_DISABLE_DISK_CACHE=1)
add_compile_definitions(QSG_INFO=1) 

# Subdirectories

# Main executable
qt_add_executable(haasp
    src/main.cpp
    src/nucleus/ai_oracle.cpp
    src/nucleus/pilot_orchestrator.cpp
    src/nucleus/git_service.cpp
    src/nucleus/associative_nexus.cpp
    src/nucleus/quantum_conduit.cpp
    src/ui/controller.cpp
    src/nucleus/ai_oracle.hpp
    src/nucleus/pilot_orchestrator.hpp
    src/nucleus/associative_nexus.hpp
    src/nucleus/git_service.hpp
    src/nucleus/quantum_conduit.hpp
    src/ui/controller.hpp
    resources.qrc
)

# QML Resources
# qt_add_resources(haasp "resources.qrc")  # Using CMAKE_AUTORCC instead

# Link libraries
target_link_libraries(haasp PRIVATE
    Qt6::Core
    Qt6::Widgets  
    Qt6::Qml
    Qt6::Quick
    Qt6::QuickControls2
    Qt6::Concurrent
    ${LIBGIT2_LIBRARIES}
    ${PROTOBUF_LIBRARIES}
    ${GRPC_LIBRARIES}
)

# Install targets
install(TARGETS haasp
    BUNDLE DESTINATION .
    RUNTIME DESTINATION bin
)