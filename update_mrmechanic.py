import sys, json, base64

with open('/tmp/mrmechanic_data.json', 'r') as f:
    data = json.load(f)

content = base64.b64decode(data['content']).decode('utf-8')

# Add shared docs section after project overview
shared_docs_section = '''

## 📚 Shared Ecosystem Documentation

**[Complete Ecosystem Documentation](docs/README.md)** - Shared documentation for all apan39 Coolify applications

This project is part of a larger ecosystem. For comprehensive information about:
- **Application architecture** and inter-service communication → `docs/SHARED_CONTEXT.md`
- **API endpoints** across all services → `docs/API_ENDPOINTS.md` 
- **Deployment procedures** and troubleshooting → `docs/DEPLOYMENT_GUIDE.md`
- **Coolify configuration** patterns → `docs/COOLIFY_CONFIG.md`

**📍 Note**: The `docs/` directory is a git submodule pointing to the shared documentation repository. Run `git submodule update --init` if it's missing.

'''

# Insert after project overview, before Architecture
insert_point = content.find('## Architecture')
if insert_point != -1:
    new_content = content[:insert_point] + shared_docs_section + content[insert_point:]
    # Encode to base64
    encoded = base64.b64encode(new_content.encode('utf-8')).decode('ascii')
    result = {'content': encoded, 'sha': data['sha']}
    print(json.dumps(result))
else:
    print(json.dumps({'error': 'Could not find insertion point'}))