/**
 * Utility functions for determining London Underground zones
 */

// Zone 1 postcodes (Central London)
const ZONE_1_POSTCODES = ["W1", "W2", "WC1", "WC2", "EC1", "EC2", "EC3", "EC4", 
                          "SW1", "SW3", "SW5", "SW7", "SW10", "N1", "N7", "E1", "E2", "SE1", "SE11"];

// Zone 2 postcodes
const ZONE_2_POSTCODES = ["W3", "W4", "W5", "W6", "W8", "W9", "W10", "W11", "W12", "W14",
                          "SW2", "SW4", "SW6", "SW8", "SW9", "SW11", "SW12", "SW13", "SW14", "SW15", 
                          "SW16", "SW17", "SW18", "NW1", "NW2", "NW3", "NW5", "NW6", "NW8", "NW10",
                          "N2", "N3", "N4", "N5", "N6", "N8", "N9", "N10", "N11", "N12", "N13", "N14", 
                          "N15", "N16", "N17", "N18", "N19", "N20", "N21", "N22",
                          "E3", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18",
                          "SE2", "SE3", "SE4", "SE5", "SE6", "SE7", "SE8", "SE9", "SE10", "SE12", "SE13", "SE14", 
                          "SE15", "SE16", "SE17", "SE18", "SE19", "SE20", "SE21", "SE22", "SE23", "SE24", 
                          "SE25", "SE26", "SE27", "SE28"];

// Zone 3 postcodes
const ZONE_3_POSTCODES = ["SW19", "SW20", "SW21", "SW22", "SW23", "SW24", "SW25", "SW26", "SW27", "SW28",
                          "NW3", "NW4", "NW7", "NW9", "NW10", "NW11",
                          "N22", "N23", "N24", "N25", "N26", "N27", "N28", "N29",
                          "E19", "E20",
                          "SE29", "SE30", "SE31", "SE32", "SE33", "SE34", "SE35", "SE36", "SE37", "SE38", "SE39", "SE40",
                          "W13", "W15", "W16", "W17", "W18", "W19", "W20",
                          "HA0", "HA1", "HA2", "HA3", "HA4", "HA5", "HA6", "HA7", "HA8", "HA9",
                          "UB1", "UB2", "UB3", "UB4", "UB5", "UB6", "UB7", "UB8", "UB9", "UB10",
                          "TW1", "TW2", "TW3", "TW4", "TW5", "TW6", "TW7", "TW8", "TW9", "TW10", "TW11", "TW12", "TW13", "TW14",
                          "KT1", "KT2", "KT3", "KT4", "KT5", "KT6", "KT7", "KT8", "KT9", "KT10",
                          "CR0", "CR2", "CR4", "CR5", "CR6", "CR7", "CR8", "CR9",
                          "BR1", "BR2", "BR3", "BR4", "BR5", "BR6", "BR7", "BR8",
                          "DA1", "DA2", "DA3", "DA4", "DA5", "DA6", "DA7", "DA8", "DA9", "DA10", "DA11", "DA12", "DA13", "DA14", "DA15", "DA16", "DA17", "DA18"];

/**
 * Get the London Underground zone (1, 2, or 3) for a clinic based on postcode
 * @param {Object} clinic - Clinic object with postcode property
 * @returns {number|null} - Zone number (1, 2, or 3) or null if not in zones 1-3
 */
export function getZone(clinic) {
  const postcode = (clinic.postcode || '').toUpperCase().trim();
  
  if (!postcode) {
    return null;
  }
  
  // Check Zone 1
  for (const pc of ZONE_1_POSTCODES) {
    if (postcode.startsWith(pc)) {
      return 1;
    }
  }
  
  // Check Zone 2
  for (const pc of ZONE_2_POSTCODES) {
    if (postcode.startsWith(pc)) {
      return 2;
    }
  }
  
  // Check Zone 3
  for (const pc of ZONE_3_POSTCODES) {
    if (postcode.startsWith(pc)) {
      return 3;
    }
  }
  
  return null; // Outside zones 1-3
}

