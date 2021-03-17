# Change Log

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