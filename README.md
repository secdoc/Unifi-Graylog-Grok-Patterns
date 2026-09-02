# Unifi-Graylog-Grok-Patterns
Grok Patterns for Graylog to Support Unfi Network App as of 8.5.1

With the update to new version of software or platforms can come some technical adjustments. One such example is with the change from Unifi Network App CEF Integrations for external logging as of 8.5.1. The new version changes the logging format of the IDS Alerts and FW Trigger logs.

If you are parsing the logs into Graylog or any other logging or SIEM system, it will be necessary to to update any parsers or regex/grok patterns. In my case, I utilize Graylog, so it was necessary to update the parsing to properly be used with dashboards and other visualizations or search queries.

If you use Graylog, this repository has updated Grok Patterns for the Unfi Network App as of 8.5.1.

In addition, the repository includes a specific Unifi CEF Parse Pipeline Rule as well as data field normalization to provide consistency with the OPNsense parsing.

# Example Graylog Unifi Integration into Dashboards

![image](https://github.com/user-attachments/assets/97687a29-6d22-4926-bcb5-4733163f89cf)


![image](https://github.com/user-attachments/assets/8d4a8cb0-ab6f-47f5-8c1f-01a8e30cc990)


## License

Dual-licensed, **attribution required** under both:

- **Code & configuration** (scripts, rules, decoders, pipelines, configs): [Apache License 2.0](LICENSE)
- **Docs, guides & diagrams** (README, docs, diagrams): [CC BY 4.0](LICENSE-docs)

See [`LICENSING.md`](LICENSING.md) and [`NOTICE`](NOTICE). Credit: Lester E. Nichols III, secdoc.tech.

## GitLab CI baseline

GitLab CI runs repository integrity validation and centralized ClamAV scanning on the isolated `phase4-untrusted` runner. The baseline validates tracked Python syntax, shell syntax, and JSON parsing without direct Internet access. Repository-specific build and test gates remain additive to this baseline.

