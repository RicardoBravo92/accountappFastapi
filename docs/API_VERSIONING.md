# API Versioning Strategy

## Overview

This document describes the versioning strategy for the AccountApp API. The goal is to ensure backward compatibility, clear communication of changes, and smooth migration paths for API consumers.

## Versioning Scheme

### URL-Based Versioning (Current)

The API uses **URL-based versioning** with the version embedded in the URL path:

```
/api/v1/...
```

- **Major versions** (v1, v2, v3) indicate breaking changes
- **Minor versions** are not used in URLs; new endpoints are added to the current version
- **Patch versions** are not exposed; they represent bug fixes and internal improvements

### Version Header (Planned)

In addition to URL versioning, the API will support the `Accept` header for version negotiation:

```
Accept: application/vnd.accountapp.v1+json
```

This allows clients to explicitly request a specific version.

## Version Lifecycle

### Current Version: v1

- **Status**: Active development
- **Support**: Full support
- **Deprecation**: Not planned

### Future Versions

| Version | Status | Expected Release | Support Period |
|---------|--------|------------------|----------------|
| v1      | Active | Current          | Until v2 + 12 months |
| v2      | Planned | TBD             | 12 months after v3 |

## Breaking Changes

The following changes are considered **breaking** and require a new major version:

- Removing or renaming endpoints
- Removing or renaming response fields
- Changing response field types
- Changing required request parameters
- Changing authentication/authorization requirements
- Changing error response format
- Changing pagination structure
- Removing or changing enum values

The following changes are **non-breaking** and can be made within the same version:

- Adding new endpoints
- Adding new optional request parameters
- Adding new response fields
- Adding new enum values
- Fixing bugs that don't change the API contract
- Improving performance
- Adding new query parameters with defaults

## Deprecation Policy

When a version is deprecated:

1. **Announcement**: 6 months advance notice via:
   - API response headers: `Deprecation: true`
   - `Sunset` header with deprecation date
   - Documentation updates
   - Email to registered API consumers

2. **Sunset Period**: 6 months from announcement
   - Deprecated version continues to work
   - New features only added to current version
   - Bug fixes applied to both versions if critical

3. **Retirement**: After sunset period
   - Version may be disabled
   - Requests return `410 Gone` with migration guide link

## Migration Guidelines

### For API Consumers

1. **Monitor Deprecation Headers**:
   ```
   Deprecation: true
   Sunset: Sat, 01 Jan 2025 00:00:00 GMT
   Link: <https://docs.accountapp.com/migration/v1-to-v2>; rel="deprecation"
   ```

2. **Test Early**: Use staging environment to test against upcoming versions

3. **Plan Migration**: Allocate time for migration before sunset date

### For API Developers

1. **Document Changes**: Maintain a `CHANGELOG.md` with version-specific changes

2. **Provide Migration Guide**: For each major version, provide:
   - Breaking changes list
   - Code examples for migration
   - Timeline

3. **Maintain Compatibility Layer**: When possible, support both versions during transition

## Implementation Details

### Current Implementation (v1)

```python
# app/main.py
settings.API_V1_STR = "/api/v1"

# app/api/v1/router.py
api_router = APIRouter()
api_router.include_router(auth_router)
# ... other routers

# app/main.py
app.include_router(api_router, prefix=settings.API_V1_STR)
```

### Planned: Version Header Support

```python
# Future implementation
from fastapi import Header

@app.get("/resource")
async def get_resource(
    accept: str = Header(None),
    api_version: str = Depends(get_api_version_from_header)
):
    # Route to appropriate version handler
    pass
```

## Version Detection

Clients can detect the API version through:

1. **URL**: `/api/v1/resource` → version 1
2. **Response Header**: `API-Version: v1`
3. **OpenAPI Spec**: Available at `/openapi.json` with version info

## Best Practices

### For Consumers

1. Always specify version in URL: `/api/v1/...`
2. Handle `410 Gone` responses gracefully
3. Monitor `Deprecation` and `Sunset` headers
4. Use the `Accept` header when available for explicit versioning

### For Developers

1. Never break existing v1 endpoints
2. Add new fields as optional
3. Use feature flags for gradual rollouts
4. Test both versions in CI/CD
5. Document all changes in `CHANGELOG.md`

## Changelog Format

```markdown
## [v1.1.0] - 2024-01-15
### Added
- GET /api/v1/reports/new-endpoint
- New field `metadata` in Company response

### Changed
- Increased rate limit for authenticated users

### Fixed
- Fixed pagination cursor encoding issue

## [v1.0.0] - 2023-06-01
### Added
- Initial API release
- Authentication endpoints
- Company, Contact, Account management
```

## Future Considerations

1. **GraphQL Endpoint**: May be added as alternative to REST
2. **Webhooks**: Versioned separately with `webhook/v1/`
3. **API Gateway**: Version routing at gateway level
4. **Client SDKs**: Versioned to match API versions

## Contact

For questions about versioning or migration:
- Email: api-support@accountapp.com
- Documentation: https://docs.accountapp.com
- Status: https://status.accountapp.com