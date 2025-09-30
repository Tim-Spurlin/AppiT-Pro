# Source files
set(SOURCES
    main.cpp
    nucleus/git_service.cpp
    nucleus/associative_nexus.cpp
    nucleus/quantum_conduit.cpp
    nucleus/ai_oracle.cpp
    nucleus/pilot_orchestrator.cpp
    ui/controller.cpp
)

set(HEADERS
    nucleus/associative_nexus.hpp
    nucleus/git_service.hpp
    nucleus/quantum_conduit.hpp
    nucleus/ai_oracle.hpp
    nucleus/pilot_orchestrator.hpp
    ui/controller.hpp
)

# Create library for the core functionality
add_library(haasp_core ${SOURCES} ${HEADERS})

target_include_directories(haasp_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/nucleus
)

target_link_libraries(haasp_core PUBLIC
    Qt6::Core
    Qt6::Network
    ${LIBGIT2_LIBRARIES}
    protobuf::libprotobuf
    gRPC::grpc++
)
