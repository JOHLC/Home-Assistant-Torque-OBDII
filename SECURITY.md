# Security Policy

## Supported Versions

Security updates are provided for the latest publicly released version of the Torque OBD-II integration.

| Version                                    | Supported          |
| ------------------------------------------ | ------------------ |
| Latest release                             | :white_check_mark: |
| Older releases                             | :x:                |
| Development branches and unreleased builds | Best effort        |

Users should update to the latest available release before reporting a vulnerability that may already have been corrected.

## Security Scope

This project is a Home Assistant custom integration that receives telemetry uploaded by the Torque Android application.

The integration is intended to be receive-only. It does not directly communicate with:

* The vehicle
* The OBD-II adapter
* The vehicle CAN bus
* Vehicle control modules
* Vehicle safety systems

It is not designed to:

* Send commands to a vehicle
* Write OBD-II or CAN bus data
* Modify ECU data
* Program vehicle modules
* Change odometer values
* Control vehicle functions

Security reports should focus on behavior introduced by this repository, including its Home Assistant endpoint, configuration flow, telemetry parsing, entity creation, data handling, authentication behavior, validation, logging, and dependencies.

## Reporting a Vulnerability

Please do not report suspected security vulnerabilities through a public GitHub issue, discussion, forum post, or pull request.

Use GitHub's private vulnerability reporting feature:

1. Open the repository on GitHub.
2. Select the **Security** tab.
3. Select **Report a vulnerability**.

Repository:

https://github.com/JOHLC/Home-Assistant-Torque-OBDII

If private vulnerability reporting is unavailable, open a public issue containing no sensitive technical details and request a private method of communication.

## Information to Include

Please provide as much of the following information as possible:

* A clear description of the vulnerability
* The affected integration version
* The affected Home Assistant version
* Required configuration or environmental conditions
* Reproduction steps
* Proof-of-concept requests or payloads
* Relevant logs with credentials, tokens, GPS coordinates, email addresses, and other sensitive information removed
* The expected behavior
* The actual behavior
* The potential security impact
* Any suggested mitigation or correction
* Whether the vulnerability has been disclosed elsewhere

Do not include real credentials, authentication tokens, private URLs, personal location history, or other sensitive information in a report.

## Response Process

The project maintainer will aim to:

* Acknowledge the report within 3 business days
* Perform an initial assessment within 7 business days
* Request additional information when needed
* Provide a status update at least every 14 days while an accepted report remains under investigation
* Coordinate a correction and disclosure timeline when appropriate

Response times may vary because this is a volunteer-maintained open-source project.

## Accepted Reports

If a report is accepted as a security vulnerability, the maintainer may:

* Confirm the affected versions
* Develop and test a correction
* Prepare a security advisory
* Request that details remain private until a fix is available
* Release an updated integration version
* Publish mitigation or upgrade instructions
* Credit the reporter, unless anonymous credit is requested

The timing of public disclosure will depend on the severity of the issue, the availability of a correction, and the risk to users.

## Declined Reports

A report may be declined when:

* The behavior cannot be reproduced
* The issue is not caused by this integration
* The report concerns unsupported or modified code
* The report describes expected behavior
* The report requires an already-compromised Home Assistant administrator account
* The issue is caused solely by insecure Home Assistant, network, reverse proxy, Android, Torque, adapter, or vehicle configuration
* The report concerns general OBD-II or CAN bus risks without a demonstrated path through this integration
* The report is a feature request, documentation issue, or ordinary software defect without a security impact

When possible, the maintainer will explain why a report was declined and may recommend a more appropriate reporting location.

## Examples of Relevant Security Issues

Examples include:

* Authentication or authorization bypasses
* Exposure of telemetry between configuration entries
* Unauthorized submission of telemetry
* Predictable or reusable endpoint identifiers that create unintended access
* Injection vulnerabilities
* Unsafe parsing of uploaded data
* Denial-of-service conditions caused by malformed or excessive requests
* Sensitive information written unnecessarily to logs
* Cross-site scripting or unsafe rendering
* Path traversal or arbitrary file access
* Leakage of credentials, tokens, email addresses, GPS data, or vehicle identifiers
* Dependency vulnerabilities that are reachable through this integration
* Behavior that allows the integration to communicate back to a vehicle or adapter unexpectedly

## Examples of Issues Usually Outside Scope

The following are generally outside the scope of this repository unless the integration directly introduces or worsens the issue:

* A publicly exposed or misconfigured Home Assistant instance
* Weak Home Assistant credentials
* Missing HTTPS for remote access
* Compromise of the Android device
* Vulnerabilities in the Torque application
* Vulnerabilities in an OBD-II adapter
* Vehicle manufacturer security weaknesses
* General CAN bus or OBD-II attack techniques
* Malicious Home Assistant administrators
* Physical access to the vehicle or adapter
* Data intentionally enabled and stored by the user
* Loss of telemetry when connectivity is unavailable
* Missing buffering or delayed upload functionality

These concerns may still be important, but they should normally be reported to the responsible project, vendor, or manufacturer.

## Security Recommendations for Users

Users should:

* Keep Home Assistant and this integration updated
* Use HTTPS for remote connections
* Use plain HTTP only on a trusted private network
* Avoid exposing Home Assistant directly to the public internet
* Use strong authentication and appropriate remote-access controls
* Protect Home Assistant backups, logs, and recorder databases
* Review recorder retention settings
* Limit GPS and other sensitive telemetry to what is necessary
* Remove credentials, identifiers, and location data before sharing logs
* Review the security of the Android device, Torque application, network, and OBD-II adapter

## Privacy Considerations

Vehicle telemetry may include sensitive information such as:

* Current GPS coordinates
* Location and trip history
* Driving patterns
* Vehicle identifiers
* Device identifiers
* Email addresses
* Fuel consumption
* Diagnostic information
* Vehicle performance data

This information may be retained by Home Assistant history, recorder databases, logs, backups, and external services configured by the user.

Users are responsible for determining what telemetry they choose to collect and how long it is retained.

## Good-Faith Security Research

Good-faith security research is welcome.

Researchers should:

* Avoid accessing data that does not belong to them
* Avoid disrupting systems or services
* Use test environments whenever possible
* Stop testing if sensitive data is encountered
* Report findings privately
* Allow reasonable time for investigation and remediation
* Avoid public disclosure before a coordinated release or advisory

Testing against systems without authorization is not permitted.

## No Security Warranty

This project is provided under the terms of its open-source license and without a guarantee that it is free from security defects.

Users remain responsible for securing their Home Assistant environment, networks, devices, applications, adapters, and vehicle-related systems.
