// London dental clinic data - includes both NHS and private practices
export const clinicsData = [
  {
    name: "Bupa Dental Care - Oxford Street",
    address: "250 Oxford Street, London W1C 1DH",
    phone: "020 7636 5678",
    services: ["General Dentistry", "Cosmetic Dentistry", "Teeth Whitening", "Dental Implants"],
    languages: ["English"],
    postcode: "W1C 1DH",
    nhs: true,
    private: true,
    emergency: true,
    children: true,
    wheelchair_access: true,
    rating: 4.5
  },
  {
    name: "MyDentist - Camden",
    address: "123 Camden High Street, London NW1 7JR",
    phone: "020 7387 1234",
    services: ["General Dentistry", "Orthodontics", "Emergency Care"],
    languages: ["English", "Polish"],
    postcode: "NW1 7JR",
    nhs: true,
    private: false,
    emergency: true,
    children: true,
    wheelchair_access: true,
    rating: 4.3
  },
  {
    name: "Smile Dental Practice - NW6",
    address: "156 Kilburn High Road, London NW6 4JD",
    phone: "020 7624 5678",
    services: ["General Dentistry", "Orthodontics", "Teeth Whitening", "Root Canal"],
    languages: ["English", "Portuguese", "Spanish"],
    postcode: "NW6 4JD",
    nhs: true,
    private: true,
    emergency: true,
    children: true,
    rating: 4.6
  },
  {
    name: "Portman Dental Care - Islington",
    address: "45 Upper Street, London N1 0PN",
    phone: "020 7359 4567",
    services: ["General Dentistry", "Cosmetic Dentistry", "Teeth Whitening", "Invisalign"],
    languages: ["English", "French"],
    postcode: "N1 0PN",
    nhs: false,
    private: true,
    emergency: false,
    children: true,
    wheelchair_access: true,
    rating: 4.7
  },
  {
    name: "Kensington Dental Practice",
    address: "156 Kensington High Street, London W8 6SH",
    phone: "020 7937 5678",
    services: ["General Dentistry", "Dental Implants", "Cosmetic Dentistry", "Teeth Whitening", "Orthodontics"],
    languages: ["English", "French", "Italian"],
    postcode: "W8 6SH",
    nhs: false,
    private: true,
    emergency: true,
    children: true,
    wheelchair_access: true,
    rating: 4.9
  }
];
