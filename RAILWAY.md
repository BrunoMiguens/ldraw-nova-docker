# Railway deployment (fork)

This branch adapts the upstream [LDraw Nova Docker app](https://github.com/anteloc/ldraw-nova-docker) for Railway. The core toolkit is fetched from the creator's repository at the commit pinned in Dockerfile. The upstream master branch is unchanged.

## Service configuration
- Source: `BrunoMiguens/ldraw-nova-docker`, branch `railway`.
- Dockerfile builder; target port 8000; health path /healthz.
- Attach one persistent volume at /persist. Data and root-only config are separate subdirectories.
- APP_USERNAME defaults to admin. Set APP_PASSWORD to a unique random password of at least 16 characters in Railway. The application fails closed without it. For a Railway template use `${{secret(32)}}` as the password default; never publish an actual secret.
- Configure model provider API keys in Railway Variables or the protected app Settings; TYPESAFE_API_KEY is optional. The localhost browser OAuth callback is not supported in this cloud configuration.
- Use Railway HTTPS; do not publish raw HTTP or additional ports.
- Intended for one trusted user, not multi-tenant hosting. The upstream app executes agent-generated code, so do not share access or run untrusted models/prompts. Back up the volume and monitor usage.

## Verification
A healthy HTTP process is not proof that rendering, AI generation or persistence work. Verify authentication, generate and render a small model, restart the service and confirm the model remains before publishing a template.

Upstream licensing and attribution remain unchanged. See the original README and LICENSE.
