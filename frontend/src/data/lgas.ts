// Sourced from 02_LGAs/ekiti_lgas.csv (generated, not hand-edited). Every row is
// still "Pending" verification in that dataset.
//
// The Explore page doesn't render this array: it fetches /api/lgas through
// /api/content/lgas. The `Lga` type is the shape that endpoint should return,
// and the array is ready-made seed data for it.

export type Lga = {
  slug: string;
  name: string;
  headquarters: string;
  latitude: number;
  longitude: number;
  towns: string[];
  notablePlaces: string[];
  institutions: string[];
  sources: { name: string; url: string }[];
  lastChecked: string;
  verificationStatus: string;
  limitations: string;
};

export const lgas: Lga[] = [
  {
    "slug": "ado-ekiti",
    "name": "Ado Ekiti",
    "headquarters": "Ado-Ekiti",
    "latitude": 7.621111,
    "longitude": 5.221389,
    "towns": [
      "Ado-Ekiti"
    ],
    "notablePlaces": [
      "Fajuyi Memorial Park",
      "Ewi of Ado-Ekiti's Palace"
    ],
    "institutions": [
      "Ekiti State University",
      "Afe Babalola University",
      "Federal Polytechnic Ado-Ekiti"
    ],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.latlong.net/place/ado-ekiti-nigeria-24847.html"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Coordinates and listed places require independent review before publication"
  },
  {
    "slug": "efon",
    "name": "Efon",
    "headquarters": "Efon-Alaaye",
    "latitude": 7.65649,
    "longitude": 4.92235,
    "towns": [
      "Efon-Alaaye"
    ],
    "notablePlaces": [
      "Efon hills"
    ],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geodatos.net/en/coordinates/nigeria/efon-alaaye"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Landmarks and coordinates require independent verification"
  },
  {
    "slug": "ekiti-east",
    "name": "Ekiti East",
    "headquarters": "Omuo-Ekiti",
    "latitude": 7.75833,
    "longitude": 5.72227,
    "towns": [
      "Omuo-Ekiti",
      "Isinbode-Ekiti",
      "Ilasa-Ekiti"
    ],
    "notablePlaces": [],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.mindat.org/feature-2325727.html"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Communities and coordinates require independent verification"
  },
  {
    "slug": "ekiti-south-west",
    "name": "Ekiti South-West",
    "headquarters": "Ilawe-Ekiti",
    "latitude": 7.6,
    "longitude": 5.1,
    "towns": [
      "Ilawe-Ekiti"
    ],
    "notablePlaces": [
      "Alawe of Ilawe's Palace"
    ],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Ilawe-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Headquarters information is supported by the official Ekiti State directory. Coordinates and landmark details remain pending."
  },
  {
    "slug": "ekiti-west",
    "name": "Ekiti West",
    "headquarters": "Aramoko-Ekiti",
    "latitude": 7.711,
    "longitude": 5.044,
    "towns": [
      "Aramoko-Ekiti",
      "Ikogosi-Ekiti",
      "Ipole-Iloro",
      "Erijiyan-Ekiti"
    ],
    "notablePlaces": [
      "Ikogosi Warm Springs",
      "Arinta Waterfall"
    ],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Aramoko-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Tourism sites and coordinates require independent verification"
  },
  {
    "slug": "emure",
    "name": "Emure",
    "headquarters": "Emure-Ekiti",
    "latitude": 7.45,
    "longitude": 5.466667,
    "towns": [
      "Emure-Ekiti"
    ],
    "notablePlaces": [
      "Elemure of Emure's Palace"
    ],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Emure-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Landmark and coordinates require independent verification"
  },
  {
    "slug": "aiyekire",
    "name": "Aiyekire",
    "headquarters": "Ode-Ekiti",
    "latitude": 7.789,
    "longitude": 5.711,
    "towns": [
      "Ode-Ekiti",
      "Aisegba-Ekiti",
      "Agbado-Ekiti",
      "Iluomoba-Ekiti"
    ],
    "notablePlaces": [],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government/aiyekire"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Ode-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Ekiti State Government uses Aiyekire as the official LGA name. Gbonyin is also used in some government and public records. Coordinates remain approximate and pending review."
  },
  {
    "slug": "ido-osi",
    "name": "Ido/Osi",
    "headquarters": "Ido-Ekiti",
    "latitude": 7.846,
    "longitude": 5.183,
    "towns": [
      "Ido-Ekiti",
      "Ifaki-Ekiti",
      "Usi-Ekiti",
      "Ayetoro-Ekiti"
    ],
    "notablePlaces": [],
    "institutions": [
      "Federal Teaching Hospital Ido-Ekiti"
    ],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Ido-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Institution and coordinates require independent verification"
  },
  {
    "slug": "ijero",
    "name": "Ijero",
    "headquarters": "Ijero-Ekiti",
    "latitude": 7.815,
    "longitude": 5.067,
    "towns": [
      "Ijero-Ekiti"
    ],
    "notablePlaces": [],
    "institutions": [
      "Ekiti State College of Health Sciences and Technology, Ijero-Ekiti"
    ],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Ijero-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Institution and coordinates require independent verification"
  },
  {
    "slug": "ikere",
    "name": "Ikere",
    "headquarters": "Ikere-Ekiti",
    "latitude": 7.498,
    "longitude": 5.232,
    "towns": [
      "Ikere-Ekiti"
    ],
    "notablePlaces": [
      "Olosunta Hills",
      "Orole Hills"
    ],
    "institutions": [
      "Bamidele Olumilua University of Education, Science and Technology"
    ],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Ikere-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Institution, landmarks and coordinates require independent verification"
  },
  {
    "slug": "ikole",
    "name": "Ikole",
    "headquarters": "Ikole-Ekiti",
    "latitude": 7.797,
    "longitude": 5.514,
    "towns": [
      "Ikole-Ekiti",
      "Odo-Ayedun-Ekiti"
    ],
    "notablePlaces": [],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Ikole-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Communities and coordinates require independent verification"
  },
  {
    "slug": "ilejemeje",
    "name": "Ilejemeje",
    "headquarters": "Eda-Oniyo-Ekiti",
    "latitude": 7.995,
    "longitude": 5.126,
    "towns": [
      "Eda-Oniyo-Ekiti"
    ],
    "notablePlaces": [],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Eda-Oniyo-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Headquarters spelling and coordinates require confirmation"
  },
  {
    "slug": "irepodun-ifelodun",
    "name": "Irepodun/Ifelodun",
    "headquarters": "Igede-Ekiti",
    "latitude": 7.668,
    "longitude": 5.126,
    "towns": [
      "Igede-Ekiti",
      "Iyin-Ekiti",
      "Iworoko-Ekiti"
    ],
    "notablePlaces": [],
    "institutions": [
      "Federal University of Technology and Environmental Sciences (FUTES), Iyin-Ekiti"
    ],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Igede-Ekiti&country=NG"
      },
      {
        "name": "Federal University of Technology Akure",
        "url": "https://www.futa.edu.ng/home/newsd/1419"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "FUTES in Iyin-Ekiti is supported by an official FUTA publication. Its operational details and exact campus coordinates still require independent verification."
  },
  {
    "slug": "ise-orun",
    "name": "Ise/Orun",
    "headquarters": "Ise-Ekiti",
    "latitude": 7.465,
    "longitude": 5.423,
    "towns": [
      "Ise-Ekiti",
      "Orun-Ekiti"
    ],
    "notablePlaces": [],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Ise-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Communities and coordinates require independent verification"
  },
  {
    "slug": "moba",
    "name": "Moba",
    "headquarters": "Otun-Ekiti",
    "latitude": 7.989,
    "longitude": 5.124,
    "towns": [
      "Otun-Ekiti",
      "Ikun-Ekiti",
      "Erinmope-Ekiti"
    ],
    "notablePlaces": [
      "Ikun Dairy Farm"
    ],
    "institutions": [],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Otun-Ekiti&country=NG"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Landmark classification, communities and coordinates require verification"
  },
  {
    "slug": "oye",
    "name": "Oye",
    "headquarters": "Oye-Ekiti",
    "latitude": 7.8,
    "longitude": 5.333,
    "towns": [
      "Oye-Ekiti",
      "Ayede-Ekiti",
      "Itapa-Ekiti",
      "Ilupeju-Ekiti",
      "Isan-Ekiti"
    ],
    "notablePlaces": [],
    "institutions": [
      "Federal University Oye-Ekiti",
      "Ekiti State Polytechnic, Isan-Ekiti"
    ],
    "sources": [
      {
        "name": "Ekiti State Government Local Government and LCDAs directory",
        "url": "https://www.ekitistate.gov.ng/about-ekiti/local-government"
      },
      {
        "name": "secondary geographic coordinate reference",
        "url": "https://www.geonames.org/search.html?q=Oye-Ekiti&country=NG"
      },
      {
        "name": "Ekiti State Polytechnic, Isan-Ekiti official website",
        "url": "https://www.ekspoly.edu.ng/"
      }
    ],
    "lastChecked": "2026-09-21",
    "verificationStatus": "Pending",
    "limitations": "Institution, communities and coordinates require independent verification. Ekiti State Polytechnic, Isan-Ekiti, is supported by the institution's official website; its exact campus coordinates still require independent verification."
  }
];
