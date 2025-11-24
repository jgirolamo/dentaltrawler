"""
Example usage of the Dental Service Trawler
"""

from dental_trawler import DentalServiceTrawler

# Create trawler instance
trawler = DentalServiceTrawler()

# Option 1: Run with default settings (from config.py)
clinics = trawler.run(location="London", max_clinics=10)

# Option 2: Scrape a specific clinic website
# clinic_data = trawler.scrape_clinic_website("https://example-dental-clinic.com")
# print(f"Services: {clinic_data['services']}")
# print(f"Languages: {clinic_data['languages']}")

# Save results
trawler.save_to_json("my_results.json")
trawler.save_to_csv("my_results.csv")

# Print some results
print(f"\nFound {len(clinics)} clinics")
for clinic in clinics[:5]:
    print(f"\n{clinic.get('name', 'Unknown')}")
    print(f"  Services: {', '.join(clinic.get('services', [])) or 'N/A'}")
    print(f"  Languages: {', '.join(clinic.get('languages', [])) or 'N/A'}")

