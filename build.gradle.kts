plugins {
    base
}

allprojects {
    group = "com.cstorestudio"
    version = "1.0.0-SNAPSHOT"
}

tasks.register<Exec>("composeUp") {
    group = "docker"
    description = "Starts all services using docker-compose"
    commandLine("docker-compose", "up", "-d")
}

tasks.register<Exec>("composeDown") {
    group = "docker"
    description = "Stops all services using docker-compose"
    commandLine("docker-compose", "down")
}
