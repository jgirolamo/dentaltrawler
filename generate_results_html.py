"""
Generate a standalone HTML file with all dental clinic results
No duplicates, all clinics displayed
"""
import json
import re

def load_clinics():
    """Load clinics from the JavaScript file"""
    import ast
    
    # Read the clinics.js file
    with open('dentaltrawler/src/clinics.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the array content
    match = re.search(r'export const clinicsData = (\[.*?\]);', content, re.DOTALL)
    if match:
        array_content = match.group(1)
        
        # Use ast.literal_eval which is safer than eval
        # But first we need to convert JS object syntax to Python dict syntax
        # Replace JS object keys (no quotes) with Python dict keys (quotes)
        # This is a simple approach - replace : with :" and add quotes before colons
        array_content = re.sub(r'(\w+):', r'"\1":', array_content)  # Add quotes to keys
        array_content = array_content.replace('true', 'True').replace('false', 'False')  # JS to Python bools
        
        try:
            clinics = ast.literal_eval(array_content)
        except:
            # Fallback: manually parse the structure
            print("Using manual parsing...")
            clinics = []
            # Find all clinic objects
            clinic_pattern = r'\{[^}]+\}'
            matches = re.findall(clinic_pattern, array_content, re.DOTALL)
            for match in matches:
                clinic = {}
                # Extract name
                name_match = re.search(r'name:\s*"([^"]+)"', match)
                if name_match:
                    clinic['name'] = name_match.group(1)
                # Extract other fields similarly
                for field in ['address', 'phone', 'postcode']:
                    field_match = re.search(f'{field}:\\s*"([^"]+)"', match)
                    if field_match:
                        clinic[field] = field_match.group(1)
                
                # Extract arrays
                services_match = re.search(r'services:\s*\[(.*?)\]', match, re.DOTALL)
                if services_match:
                    services = re.findall(r'"([^"]+)"', services_match.group(1))
                    clinic['services'] = services
                
                languages_match = re.search(r'languages:\s*\[(.*?)\]', match, re.DOTALL)
                if languages_match:
                    languages = re.findall(r'"([^"]+)"', languages_match.group(1))
                    clinic['languages'] = languages
                
                # Extract booleans
                for field in ['private', 'emergency', 'children', 'wheelchair_access']:
                    if re.search(f'{field}:\\s*true', match):
                        clinic[field] = True
                    elif re.search(f'{field}:\\s*false', match):
                        clinic[field] = False
                
                # Extract rating
                rating_match = re.search(r'rating:\s*([\d.]+)', match)
                if rating_match:
                    clinic['rating'] = float(rating_match.group(1))
                
                if clinic.get('name'):
                    clinics.append(clinic)
    
    return clinics

def remove_duplicates(clinics):
    """Remove duplicate clinics based on name and postcode"""
    seen = set()
    unique_clinics = []
    
    for clinic in clinics:
        # Create a unique key from name and postcode
        key = (clinic.get('name', '').lower().strip(), clinic.get('postcode', '').upper().strip())
        
        if key not in seen and key[0] and key[1]:  # Only add if both name and postcode exist
            seen.add(key)
            unique_clinics.append(clinic)
    
    return unique_clinics

def generate_html(clinics):
    """Generate standalone HTML file with all clinics"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>London Private Dental Clinics - All Results</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .stats {
            color: #7f8c8d;
            font-size: 14px;
        }
        .search-box {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        #searchInput {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 4px;
        }
        #searchInput:focus {
            outline: none;
            border-color: #3498db;
        }
        .results {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        .clinic-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .clinic-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .clinic-name {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .clinic-info {
            color: #7f8c8d;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .clinic-info strong {
            color: #34495e;
        }
        .services, .languages {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #ecf0f1;
        }
        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }
        .tag {
            background: #3498db;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
        }
        .tag.language {
            background: #9b59b6;
        }
        .tag.feature {
            background: #27ae60;
        }
        .rating {
            color: #f39c12;
            font-weight: bold;
        }
        .no-results {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 London Private Dental Clinics</h1>
            <div class="stats">
                <span id="totalCount">""" + str(len(clinics)) + """</span> clinics found
            </div>
        </header>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search by name, address, postcode, service, or language...">
        </div>
        
        <div class="results" id="results">
"""
    
    # Add clinic cards
    for clinic in clinics:
        services_html = ''.join([f'<span class="tag">{s}</span>' for s in clinic.get('services', [])])
        languages_html = ''.join([f'<span class="tag language">{l}</span>' for l in clinic.get('languages', [])])
        
        features = []
        if clinic.get('emergency'): features.append('Emergency')
        if clinic.get('children'): features.append('Children')
        if clinic.get('wheelchair_access'): features.append('Wheelchair Access')
        features_html = ''.join([f'<span class="tag feature">{f}</span>' for f in features])
        
        html += f"""
            <div class="clinic-card" data-name="{clinic.get('name', '').lower()}" 
                 data-address="{clinic.get('address', '').lower()}" 
                 data-postcode="{clinic.get('postcode', '').lower()}"
                 data-services="{' '.join([s.lower() for s in clinic.get('services', [])])}"
                 data-languages="{' '.join([l.lower() for l in clinic.get('languages', [])])}">
                <div class="clinic-name">{clinic.get('name', 'Unknown')}</div>
                <div class="clinic-info"><strong>📍</strong> {clinic.get('address', 'N/A')}</div>
                <div class="clinic-info"><strong>📞</strong> {clinic.get('phone', 'N/A')}</div>
                <div class="clinic-info"><strong>📮</strong> {clinic.get('postcode', 'N/A')}</div>
                {f'<div class="clinic-info rating">⭐ {clinic.get("rating", 0)}/5.0</div>' if clinic.get('rating') else ''}
                <div class="services">
                    <strong>Services:</strong>
                    <div class="tags">{services_html}</div>
                </div>
                <div class="languages">
                    <strong>Languages:</strong>
                    <div class="tags">{languages_html}</div>
                </div>
                {f'<div class="tags" style="margin-top: 10px;">{features_html}</div>' if features else ''}
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <script>
        const searchInput = document.getElementById('searchInput');
        const results = document.getElementById('results');
        const totalCount = document.getElementById('totalCount');
        const cards = document.querySelectorAll('.clinic-card');
        
        function filterResults() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            let visibleCount = 0;
            
            cards.forEach(card => {
                const name = card.dataset.name || '';
                const address = card.dataset.address || '';
                const postcode = card.dataset.postcode || '';
                const services = card.dataset.services || '';
                const languages = card.dataset.languages || '';
                
                const matches = !searchTerm || 
                    name.includes(searchTerm) ||
                    address.includes(searchTerm) ||
                    postcode.includes(searchTerm) ||
                    services.includes(searchTerm) ||
                    languages.includes(searchTerm);
                
                if (matches) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            totalCount.textContent = visibleCount;
            
            // Show no results message if needed
            let noResults = results.querySelector('.no-results');
            if (visibleCount === 0 && searchTerm) {
                if (!noResults) {
                    noResults = document.createElement('div');
                    noResults.className = 'no-results';
                    noResults.textContent = 'No clinics found matching your search.';
                    results.appendChild(noResults);
                }
            } else if (noResults) {
                noResults.remove();
            }
        }
        
        searchInput.addEventListener('input', filterResults);
    </script>
</body>
</html>
"""
    
    return html

def main():
    print("Loading clinics...")
    clinics = load_clinics()
    print(f"Loaded {len(clinics)} clinics")
    
    print("Removing duplicates...")
    unique_clinics = remove_duplicates(clinics)
    print(f"Found {len(unique_clinics)} unique clinics")
    
    print("Generating HTML...")
    html = generate_html(unique_clinics)
    
    output_file = "all_clinics_results.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Generated {output_file} with {len(unique_clinics)} unique clinics")
    print(f"✅ Open {output_file} in your browser to view all results")

if __name__ == "__main__":
    main()

