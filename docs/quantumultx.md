# Quantumult X setup

## Starter profile

1. Save a backup of your existing Quantumult X configuration in the app.
2. Download the `basic.conf` asset from the project's latest GitHub release
   and import it as a configuration in Quantumult X.
3. Add your own working servers or a Quantumult X-compatible subscription.
4. In the `Proxy` policy group, switch from `direct` to the built-in `proxy`
   policy, then select the intended server in Quantumult X.
5. Enable rule/filter mode and check the request log for the selected policies.

There are no bundled nodes or subscription credentials. Before step 4, the
starter deliberately uses direct connections. AI, Streaming, Social and Global
point to Proxy; Apple and China default to direct. The China GeoIP fallback
uses the client's database, not a downloaded third-party ruleset in this repo.
Unmatched traffic uses Global. Private-network fallbacks use direct.

The starter uses network-provided DNS and does not configure MITM, scripts,
rewrites or remote parsers. Adjust DNS to your own network requirements.
The small starter lists do not cover every CDN, login endpoint or service
subdomain; a category label is not a guarantee of complete service coverage.

The rules are embedded: a downloaded profile is a snapshot. Import a newer
release to update that snapshot, preserving your personal node settings.
Do not put personal settings back into this repository's generated `dist/`.

## Remote lists in an existing configuration

Each list contains native rules with category policy names. When using a list
in another configuration, override those names with an existing policy:

```ini
[filter_remote]
https://raw.githubusercontent.com/lonecoding/lonerules/main/dist/quantumultx/rules/AI.list, tag=LoneRules-AI, force-policy=proxy, enabled=true
```

Here `proxy` is Quantumult X's built-in policy and requires your own servers.
Replace it with your own policy name if desired. For a fixed version replace
`main` in the URL with `v0.1.0`. Main tracks reviewed source updates; GitHub raw
responses may be cached. Avoid adding the same list on top of its embedded
rules unless you intentionally manage precedence.

The remaining files are `Apple.list`, `Streaming.list`, `Social.list`,
`China.list` and `Global.list` under the same directory. Use `force-policy=direct`
for Apple/China if you want the starter defaults.

## Validation status and device smoke test

The implementation was checked against the official
[sample configuration](https://github.com/crossutility/Quantumult-X/blob/master/sample.conf)
and [filter snippet](https://github.com/crossutility/Quantumult-X/blob/master/filter.snippet).
No official standalone Quantumult X parser is bundled. The test suite checks
our rendering, mappings, policy references and generated artifacts; it cannot
verify the iOS application's parser or actual network behavior.

**At v0.1.0 publication, device import and live routing are unverified.**
To record a device verification, test and report:

- Quantumult X version/build and iOS version.
- Import completes without configuration errors.
- Your own server works independently of this ruleset.
- `chatgpt.com` matches AI, `apple.com` matches Apple, and `github.com` matches Global.
- Switching Proxy changes the selected path in the request log.
- Local network access and a remote `.list` import work as expected.

Check policy selection, rather than treating a website loading as proof of
correct routing. Report failures with redacted log details in a GitHub issue.
