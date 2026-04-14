---
bundle:
  name: amplifier-tester
  version: 0.1.0
  description: Validates Amplifier ecosystem changes in isolated DTU environments

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: amplifier-tester:behaviors/amplifier-tester
---
