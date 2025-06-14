# DD2525 Computer Security Labs

This repository contains implementations and reports for three security lab assignments from the DD2525 Computer Security course at KTH, covering information flow control, web application security, and Android security vulnerabilities.

---

## Lab 1: Information Flow Control

**Technology:** Troupe programming language

Implementation of a dating service demonstrating information flow control mechanisms. The system includes:

- A server that handles client profiles and matching operations
- Benign clients for legitimate usage
- A malicious client that exploits the agent system to leak security labels via broadcast interception

**Key Features:**

- Server with declassification operations for profile matching  
- Benign clients with proper security label handling  
- Malicious agent demonstrating privacy attacks through label leakage  
- Mitigation strategies using permission-protected broadcasts  

**Running Instructions:**

```bash
# Pull the latest Troupe Docker image
docker pull ghcr.io/troupelang/troupe:latest

# Run a container with the project mounted
docker run -it --entrypoint=/bin/bash -v "$(pwd)":/code ghcr.io/troupelang/troupe

# Inside the container, build and run the dating server
cd /code && make dating-server

# Run the dating client
cd /dating && make dating-client

# Runt he malicious client
cd /dating && make dating-malicious
```
---


## Lab 2: Web Application Security

**Technology:** Node.js, Express.js, MongoDB, Redis, Docker

Analysis and exploitation of critical vulnerabilities in a forum web application ("Forumerly"), followed by mitigation implementations.

**Vulnerabilities Covered:**

- **ReDoS:** Exploiting regex matching for denial-of-service  
- **Web Side Channels:** Inference attacks via observable storage behavior  
- **XSS:** Persistent JavaScript injection with CSP bypass  
- **RCE:** Prototype pollution leading to remote shell execution  

**Running Instructions:**

```bash
# Install dependencies
cd forumerly
npm clean-install
```

```bash
# Start required backend services
./launch.sh
```

```bash
# Run the Node.js web server
node app.js
```

- Access the app at: [http://localhost:3000](http://localhost:3000)  
- Exploitation scripts can be found in the `exploitation_scripts/` directory. For example:

```bash
python3 exploitation_scripts/redos_exploit.py
python3 exploitation_scripts/side_channel_scraper.py
```

**Notes:**

- Use `wipe.sh` to reset the DB and services.
- Use `stop.sh` to stop services without deletion.
- Ensure ports `3000`, `6379`, `8087`, and `27017-27019` are free before running.

---

## Lab 3: Android Security

**Technology:** Android Studio (API Level 28), ADB, Docker

Security evaluation of Android apps through implementation and exploitation of inter-app communication vulnerabilities.

**Vulnerabilities Covered:**

- **Intent Sniffing:** Unauthorized reading of location broadcasts  
- **Confused Deputy:** Abuse of privileged components for data manipulation  
- **Leaky Content Provider:** Exploit of openFile method for path traversal  
- **Timing Attacks:** Inference of user location via RTT delays in messenger  

**Running Instructions:**

1. Install Android Studio and JDK 8+
2. Create an AVD using "Medium Phone" and API 28 (x86 image)
3. Import each vulnerable and exploit app as separate projects
4. Use ADB to push files to the emulator (for Task 3)
5. For the messenger server (Task 4):

```bash
./launch.sh  # Starts Docker server for timing attack experiment
```

6. For logging and RTT analysis, use:

```bash
adb logcat
```

**Additional Notes:**

- Make sure emulator has an active route for live location updates (Task 1).
- Content provider and confused deputy exploits use custom apps interacting via Intents.
- Timing attack data is analyzed against predefined RTTs to infer user regions.

---

## Security Mitigations

Each lab includes defensive strategies:

- **Information Flow Control:** Permission-based broadcasts, explicit intents  
- **Web Security:** Input validation, CSP hardening, file/mime type checks  
- **Android Security:** Secure component declarations, path validation, permission checks  

---

## Technical Implementation

These labs showcase applied security research, covering:

- Vulnerability discovery  
- Exploit development  
- Defensive programming  

All implementations follow responsible disclosure principles and are well documented.

---

## Reports

Detailed reports are provided in each lab’s directory, including:

- Vulnerability analyses  
- Exploitation techniques  
- Security recommendations
