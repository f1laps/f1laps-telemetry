# Change Log


## 2.0.4 - INSERTDATEHERE

Supporting UDP Broadcast mode & fixing last lap import issue.

### Fixed
- The last lap of a 25%+ race now gets imported correctly

## Added
- Support for UDP Broadcast mode


## 2.0.3 - 2021-07-26

Fixed minor telemetry data and logging issues

### Fixed
- Telemetry data is now correctly removing practice outlaps
- Unsupported F1 game versions are now handled gracefully
- Session History log lines are now muted


## 2.0.2 - 2021-07-18

Patching UDP bugs related to session and telemetry data.

### Changed
- Deprecated Session History packet usage because it's unreliable
- Log Flashback event data because it seems inconsistent

### Added
- The app now auto-starts telemetry when an API key is set
- When you switch from one game to the other, the app now switches in-flight without having to restart

### Fixed
- Telemetry data is now correctly populated for all laps (added session type to telemetry)
- Flashbacks are now based on the event data, which leads to more reliable flashback handling


## 2.0.1 - 2021-07-13

Early F1 2021 bug fixes.

### Fixed
- Team names are now properly retrieved and synced
- AI difficulty is now properly retrieved and synced


## 2.0.0 - 2021-07-10

Support for F1 2021 and major refactoring.

### Added
- Now supporting the F1 2021 game


## 1.0.0 - 2021-05-13

First major stable version.

### Added
- The API key and F1Laps subscription now gets validated before the session starts
- Multiplayer sessions now get flagged as such and mapped to "Multiplayer" game mode in F1Laps

### Changed
- Telemetry data for single laps (time trial) gets sent as string
- Telemetry data will only be saved if the user's subscription plan supports it
- Q3 sessions properly get mapped as Q3, not as generic "qualifying"


## 0.2.1 - 2021-04-14

Improving app performance by pushing telemetry data as string, not JSON

### Changed
- Telemetry data now gets sent as string, not JSON

### Fixed
- The link to upgrade the app when a new version is available now works


## 0.2.0 - 2021-04-05

This version supports car telemetry data sync.

### New
- Car telemetry is now pushed into F1Laps
- Q1 and Q2 sessions can now be assigned to seasons in F1Laps
- Lap status (invalid / valid) is now saved in F1Laps

### Fixed
- Spectator mode won't break the app


## 0.1.5 - 2021-03-17

Sessions will now be correctly posted even if you re-start the app during a session.

### Fixed
- Session with existing UDP Session UID error response now are handled properly (HTTP 400 instead of HTTP 403)


## 0.1.4 - 2021-03-08
 
Now your API key will be saved in a separate config file after initial entry.

### Added
- When you've entered an API key once, it will be shown again the next time you open the program. A second file called "f1laps_configuration.txt" is created in the same folder that the program itself is stored. You can safely delete or move this file anytime.

### Changed
- The version check field now displays pre-release versions
- UI: added F1Laps logo, horizontal lines and more vertical spacing


## 0.1.3 - 2021-03-03
 
Now providing a separate debugging executable too.

### Added
- A separate console executable for easier debugging will now be provided too
- The app now checks for the most recent version and recommends upgrading

### Changed
- UI cleanup incl. clearer indication when app is running


## 0.1.2 - 2021-02-28
 
Local app information now sent to F1Laps for debugging; potential fixes for app crashes.
 
### Added
- The version and OS name are now passed to F1Laps via custom headers for easier support

### Changed
- The logging field was moved to a separate console window. While this is a slightly worse user interface experience, we believe it to fix some random app crashes.
 

## 0.1.1 - 2021-02-25
 
Beta testing bug fixes, cleanup, stability and more.
 
### Added
- The executable version is now shown in the GUI.

### Changed
- Logged text window auto scrolls with new log messages
- App built with --noconsole, and without --uac-admin; which seems more stable
- Cleaned up logged text 
 

## 0.1.0 - 2021-02-24
  
Initial app version.