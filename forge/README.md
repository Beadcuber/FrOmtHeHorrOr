# Vivian Forge 1.20.1

This is a separate ForgeGradle 6 project targeting Minecraft 1.20.1 / Forge 47.2.0 / Java 17. It is kept on the `forge-1.20.1-port` branch so the working Fabric project on `main` remains unchanged.

## Build
Run `gradle build` from this directory. GitHub Actions also builds the project and uploads the Forge JAR as the `Vivian-Forge-1.20.1` artifact.

## Port status
The Forge-native bootstrap, entity/item registries, starter flashlight, spawn eggs, basic following/hostile entity behavior, client model/renderer, carry-item re-deployment, chat hook, and summon commands are in the first implementation pass.

This is not yet a feature-complete port of the Fabric build. The 44-message conversation memory, optional external AI configuration, full emotional dialogue/mood persistence, three-cycle transformation manager, music command, world-awareness features, and structure generation still need to be ported and tested before calling the Forge version complete.
