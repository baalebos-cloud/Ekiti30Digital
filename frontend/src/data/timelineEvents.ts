// Sourced from 03_Timeline/EKITI30_Timeline_Events_1996-2026.csv (Member 4,
// Research & History — PR #10, merged into main). Field names map to the
// CSV columns: date_display -> date, event_title -> title,
// verification_status -> status, source/source_link -> source/sourceUrl.
//
// verification_status values used as-is from the dataset:
// "Verified" | "Single source" | "Needs primary source" | "Conflicting sources"
//
// This file is a static snapshot for the initial launch. Once the backend's
// /api/timeline endpoint is ingesting this dataset (see ARCHITECTURE.md),
// this should be replaced with a fetch call rather than edited by hand.

export type VerificationStatus =
  | "Verified"
  | "Single source"
  | "Needs primary source"
  | "Conflicting sources";

export type TimelineEvent = {
  id: string;
  date: string;
  title: string;
  description: string;
  category: string;
  status: VerificationStatus;
  source: string;
  sourceUrl: string;
};

export const timelineEvents: TimelineEvent[] = [
  {
    id: "EK-001",
    date: "1 Oct 1996",
    title: "Ekiti State created from Ondo State",
    description:
      "Ekiti State was created out of Ondo State on 1 October 1996, with Ado-Ekiti as its capital. The state government says it was created alongside five other states and began with 16 Local Government Areas.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: About Ekiti",
    sourceUrl: "https://www.ekitistate.gov.ng/?p=444",
  },
  {
    id: "EK-002",
    date: "7 Oct 1996 – Aug 1998",
    title: "Lt. Col. Mohammed Bawa becomes first military administrator",
    description:
      "Lt. Col. Mohammed Bawa was the first Administrator of Ekiti State, serving from 7 October 1996 to August 1998.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-004",
    date: "Jul 1998",
    title: "Federal Medical Centre, Ido-Ekiti established",
    description:
      "The Federal Medical Centre in Ido-Ekiti was established in July 1998 from the Ido-Ekiti General Hospital, which dated from 1954.",
    category: "Health",
    status: "Needs primary source",
    source: "Afe Babalola University: Background History of the FMC, Ido-Ekiti",
    sourceUrl: "https://www.abuad.edu.ng/hospital-facilities/",
  },
  {
    id: "EK-003",
    date: "Aug 1998 – 29 May 1999",
    title: "Navy Capt. Atanda Yusuf becomes administrator",
    description:
      "Navy Captain Atanda Yusuf was Administrator of Ekiti State from August 1998 until civilian rule began on 29 May 1999.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-005",
    date: "29 May 1999 – 29 May 2003",
    title: "Niyi Adebayo becomes first elected civilian governor",
    description:
      "Otunba Niyi Adebayo of the Alliance for Democracy was Ekiti's first elected civilian governor, serving from 29 May 1999 to 29 May 2003.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-006",
    date: "1 Jun 1999",
    title: "State House of Assembly complex inaugurated",
    description:
      "The complex housing the Ekiti State House of Assembly, built during Atanda Yusuf's time as administrator, was inaugurated by Governor Adebayo.",
    category: "Infrastructure",
    status: "Needs primary source",
    source: "Wikipedia: Atanda Yusuf (citing ThisDay, 9 Jan 2010)",
    sourceUrl: "https://en.wikipedia.org/wiki/Atanda_Yusuf",
  },
  {
    id: "EK-007",
    date: "29 May 2003 – 19 Oct 2006",
    title: "Ayo Fayose becomes governor (first term)",
    description:
      "Ayo Fayose of the PDP took office on 29 May 2003 after defeating Niyi Adebayo. The official list gives the end of this tenure as 19 October 2006.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-008",
    date: "21–27 Mar 2006",
    title: "National population census conducted; Ekiti totals reported differently",
    description:
      "The national census was conducted between 21 and 27 March 2006. Sources give three different population totals for Ekiti State.",
    category: "Other",
    status: "Conflicting sources",
    source: "Federal Government of Nigeria Gazette (2 Feb 2009)",
    sourceUrl:
      "https://archive.gazettes.africa/archive/ng/2009/ng-government-gazette-dated-2009-02-02-no-2.pdf",
  },
  {
    id: "EK-009",
    date: "Oct 2006 (day disputed)",
    title: "Governor Fayose impeached by the House of Assembly",
    description:
      "The Ekiti State House of Assembly impeached Governor Ayo Fayose in October 2006. The state's official list says the Federal Government declared his brief replacement by the Speaker illegal.",
    category: "Government",
    status: "Conflicting sources",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-010",
    date: "19 Oct 2006 – 27 Apr 2007",
    title: "Tunji Olurin appointed administrator after state of emergency",
    description:
      "Tunji Olurin served as Administrator of Ekiti State from 19 October 2006 to 27 April 2007, appointed after a state of emergency was declared in the state.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-011",
    date: "27 Apr – 29 May 2007",
    title: "Tope Ademiluyi serves as acting governor",
    description:
      "Chief Tope Ademiluyi was Acting Governor of Ekiti State from 27 April to 29 May 2007.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-012",
    date: "29 May 2007",
    title: "Segun Oni sworn in as governor",
    description:
      "Segun Oni of the PDP, declared winner of the April 2007 election, was sworn in on 29 May 2007. Kayode Fayemi challenged the result at the election tribunal.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-013",
    date: "2009",
    title: "Afe Babalola University established in Ado-Ekiti",
    description:
      "Afe Babalola University (ABUAD), a private non-profit university, was established in Ado-Ekiti in 2009.",
    category: "Education",
    status: "Verified",
    source: "Times Higher Education: Afe Babalola University profile",
    sourceUrl:
      "https://www.timeshighereducation.com/world-university-rankings/afe-babalola-university",
  },
  {
    id: "EK-046",
    date: "17 Feb – 6 May 2009",
    title:
      "Appeal Court voids part of 2007 result; Tunji Odeyemi acting governor; Oni returns after rerun",
    description:
      "On 17 February 2009 the Court of Appeal nullified the 2007 result in part and ordered reruns in 10 of the 16 LGAs. Speaker Tunji Odeyemi served as acting governor until 6 May 2009, when Segun Oni was sworn in again after the rerun.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-014",
    date: "15–16 Oct 2010",
    title: "Court of Appeal ends Oni's tenure; Kayode Fayemi sworn in",
    description:
      "On 15 October 2010 the Court of Appeal, sitting in Kwara State, declared Kayode Fayemi the duly elected governor of the 2007 election, ending Oni's tenure. Fayemi was sworn in on 16 October 2010.",
    category: "Government",
    status: "Verified",
    source: "Vanguard: Ekiti: How Fayemi became governor (16 Oct 2010)",
    sourceUrl: "https://www.vanguardngr.com/2010/10/ekiti-how-fayemi-became-governor/",
  },
  {
    id: "EK-016",
    date: "2011",
    title: "University of Ado-Ekiti renamed Ekiti State University",
    description:
      "The University of Ado-Ekiti became Ekiti State University (EKSU) in 2011.",
    category: "Education",
    status: "Needs primary source",
    source: "Wikipedia: Ekiti State University",
    sourceUrl: "https://en.wikipedia.org/wiki/Ekiti_State_University",
  },
  {
    id: "EK-017",
    date: "2011",
    title: "Federal University Oye-Ekiti established",
    description: "Federal University Oye-Ekiti (FUOYE) was established in 2011.",
    category: "Education",
    status: "Verified",
    source: "Federal University Oye-Ekiti: official website",
    sourceUrl: "https://fuoye.edu.ng/",
  },
  {
    id: "EK-015",
    date: "Jul 2011",
    title: "Rehabilitation of Ikogosi Warm Springs Resort begins",
    description:
      "The Fayemi administration began rehabilitating the Ikogosi Warm Springs Resort, which had suffered years of neglect, in July 2011.",
    category: "Tourism",
    status: "Single source",
    source: "Ekiti State Government: The re-birth of Ikogosi Warm Springs Resort",
    sourceUrl: "https://www.ekitistate.gov.ng/archives/3943",
  },
  {
    id: "EK-018",
    date: "25 Oct 2011",
    title: "Ekiti launches Social Security Scheme for the elderly",
    description:
      "Monthly payments of N5,000 to indigent citizens aged 65 and above began on 25 October 2011, starting with about 10,000 beneficiaries at Ise-Ekiti and later rising to around 20,000.",
    category: "Government",
    status: "Verified",
    source:
      "Ekiti State Government: Ekiti Marks 2nd Anniversary Of Social Security For Elderly Citizens",
    sourceUrl: "https://www.ekitistate.gov.ng/?p=9102",
  },
  {
    id: "EK-019",
    date: "Mar 2012 (day inferred)",
    title: "Social Security Scheme backed by law",
    description:
      "Governor Fayemi signed the Social Security bill into law in March 2012, giving the elderly-stipend scheme legal backing.",
    category: "Government",
    status: "Single source",
    source: "Ekiti State Government: Fayemi Signs Social Security Bill To Law",
    sourceUrl: "https://www.ekitistate.gov.ng/?p=1763",
  },
  {
    id: "EK-020",
    date: "Oct 2012 (inferred)",
    title: "Redeveloped Ikogosi resort opened to the public",
    description:
      "The refurbished Ikogosi resort was opened to the public around October 2012, marking the second year of the Fayemi administration. Full operations were announced for April 2013.",
    category: "Tourism",
    status: "Single source",
    source: "Ekiti State Government: Ikogosi Warm Spring Resort feature",
    sourceUrl: "https://www.ekitistate.gov.ng/?p=5909",
  },
  {
    id: "EK-021",
    date: "12 Aug 2013 (stated by governor)",
    title: "Ekiti Knowledge Zone conceived",
    description:
      "Governor Oyebanji has stated that the Ekiti Knowledge Zone, a technology and innovation hub, was conceived on 12 August 2013 under Governor Fayemi. TechCabal independently dates the blueprint to 2013.",
    category: "Technology",
    status: "Single source",
    source: "Ekiti State Government: Ekiti Knowledge Zone sod-turning report",
    sourceUrl: "https://www.ekitistate.gov.ng/archives/33184",
  },
  {
    id: "EK-022",
    date: "21 Jun 2014",
    title: "Fayose wins 2014 governorship election, defeating incumbent Fayemi",
    description:
      "In INEC's declaration of results for the Ekiti governorship election held on 21 June 2014, Ayo Fayose (PDP) was declared elected with 203,090 votes, ahead of Kayode Fayemi (APC) with 120,433.",
    category: "Government",
    status: "Verified",
    source: "INEC: Declaration of Results, Ekiti State Governorship Election, June 21, 2014",
    sourceUrl:
      "https://www.inecnigeria.org/wp-content/uploads/2019/02/DECLARATION-EKITI-STATE-GOV-ELECTION-RESULT-1.pdf",
  },
  {
    id: "EK-047",
    date: "15 Oct – 15 Nov 2014",
    title: "FMC Ido-Ekiti approved as teaching hospital for ABUAD students",
    description:
      "President Goodluck Jonathan approved, in a letter dated 15 October 2014, the upgrade of the Federal Medical Centre, Ido-Ekiti, to a Federal Teaching Hospital for the clinical training of Afe Babalola University students for ten years. ABUAD signed a memorandum of understanding with the hospital on 15 November 2014.",
    category: "Health",
    status: "Single source",
    source: "Afe Babalola University: Jonathan upgrades FMC, Ido-Ekiti to Teaching Hospital Status",
    sourceUrl: "https://www.abuad.edu.ng/jonathan-upgrades-fmc-ido-ekiti-to-teaching-hospital-status/",
  },
  {
    id: "EK-023",
    date: "16 Oct 2014 – 16 Oct 2018",
    title: "Ayo Fayose's second term begins",
    description:
      "The official list gives Ayo Fayose's second term as 16 October 2014 to 16 October 2018.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-024",
    date: "14 Apr 2015",
    title: "Supreme Court dismisses APC appeal, affirming Fayose's 2014 victory",
    description:
      "On 14 April 2015 the Supreme Court dismissed the APC's appeal against Ayo Fayose's victory in the June 2014 governorship election. Reports say it held that impeachment is not a ground for disqualification under section 182 of the Constitution and that the 2006 impeachment panel was illegally constituted.",
    category: "Government",
    status: "Needs primary source",
    source:
      "BusinessDay: Supreme Court dismisses APC's appeal, affirms Ayo Fayose governor (14 Apr 2015)",
    sourceUrl:
      "https://businessday.ng/uncategorized/article/supreme-court-dismisses-apcs-appeal-affirms-ayo-fayose-governor/",
  },
  {
    id: "EK-025",
    date: "2016",
    title: "Ekiti State Health Insurance Scheme law signed",
    description:
      "The state government states that it signed into law the bill establishing the Ekiti State Health Insurance Scheme.",
    category: "Health",
    status: "Single source",
    source: "Ekiti State Government: Ekiti Health Insurance Scheme page",
    sourceUrl: "https://www.ekitistate.gov.ng/ekhis/",
  },
  {
    id: "EK-026",
    date: "29 Aug 2016",
    title: "Anti-open grazing law signed",
    description:
      "Governor Fayose signed the Prohibition of Cattle and Other Ruminants Grazing in Ekiti Law, 2016, restricting grazing to set hours and designated areas, after an attack in Oke-Ako, Ikole LGA.",
    category: "Government",
    status: "Needs primary source",
    source: "Ripples Nigeria: Fayose's anti-grazing law stirs controversy",
    sourceUrl: "https://ripplesnigeria.com/fayoses-anti-grazing-law-stirs-controversy",
  },
  {
    id: "EK-027",
    date: "Oct 2017",
    title: "ABUAD Teaching Hospital (400 beds) inaugurated",
    description:
      "The 400-bed Afe Babalola University Teaching Hospital in Ado-Ekiti was inaugurated in October 2017. Vice President Yemi Osinbajo was represented by Health Minister Prof. Isaac Adewole.",
    category: "Health",
    status: "Single source",
    source: "Afe Babalola University: Osinbajo inaugurates ABUAD Teaching Hospital",
    sourceUrl: "https://www.abuad.edu.ng/?p=11856",
  },
  {
    id: "EK-028",
    date: "14–15 Jul 2018",
    title: "Fayemi declared winner of governorship election",
    description:
      "The governorship election was held on 14 July 2018. On 15 July INEC's chief returning officer declared Kayode Fayemi (APC) the winner with 197,459 votes against 178,121 for Kolapo Olusola (PDP).",
    category: "Government",
    status: "Needs primary source",
    source: "Channels TV: INEC Announces Ekiti Governorship Election Results (15 Jul 2018)",
    sourceUrl:
      "https://www.channelstv.com/2018/07/15/inec-announces-ekiti-governorship-election-results-full-list/",
  },
  {
    id: "EK-029",
    date: "16 Oct 2018 – 16 Oct 2022",
    title: "Kayode Fayemi's second term",
    description:
      "The official list gives Kayode Fayemi's second term as 16 October 2018 to 16 October 2022.",
    category: "Government",
    status: "Verified",
    source: "Ekiti State Government: Past Governors",
    sourceUrl: "https://www.ekitistate.gov.ng/about-ekiti/past-governors",
  },
  {
    id: "EK-030",
    date: "Late 2019",
    title: "Construction of Ekiti airport begins",
    description:
      "Construction of the airport in Ado-Ekiti, later named the Ekiti Agro-Allied International Cargo Airport, began in late 2019 under Governor Fayemi.",
    category: "Infrastructure",
    status: "Verified",
    source: "ch-aviation: Ado Ekiti opens for first commercial flights",
    sourceUrl:
      "https://www.ch-aviation.com/news/161786-ado-ekiti-nigeria-opens-for-first-commercial-flights",
  },
  {
    id: "EK-031",
    date: "2020",
    title:
      "College of Education, Ikere-Ekiti upgraded to a university (now BOUESTI)",
    description:
      "Governor Fayemi signed into law in 2020 the bill upgrading the College of Education, Ikere-Ekiti (established 5 December 1977) to a university. By January 2021 it was operating as Bamidele Olumilua University of Education, Science and Technology.",
    category: "Education",
    status: "Verified",
    source:
      "Nigerian NewsDirect: Newly-established Bamidele Olumilua Varsity gets VC, Registrar",
    sourceUrl:
      "https://nigeriannewsdirect.com/newly-established-bamidele-olumilua-varsity-gets-vc-registrar-others-2/",
  },
  {
    id: "EK-036",
    date: "2022 or 2023 (unresolved)",
    title: "Ikogosi Warm Springs Resort placed under private concession",
    description:
      "The state handed management of the Ikogosi resort to Glocient Hospitality Limited, a Cavista Holdings subsidiary, under a 15-year build-operate-transfer concession.",
    category: "Tourism",
    status: "Conflicting sources",
    source: "THISDAY: Glocient Hospitality Urges Tourists to Visit Ikogosi (22 Jul 2023)",
    sourceUrl:
      "https://thisdaylive.com/index.php/2023/07/22/glocient-hospitality-urges-tourists-to-visit-ikogosi",
  },
  {
    id: "EK-037",
    date: "2022–2023 (unresolved)",
    title: "Ido-Ekiti listed among four new federal teaching hospitals",
    description:
      "A National Assembly Act created new Federal Teaching Hospitals, including one at Ido, according to Voice of Nigeria.",
    category: "Health",
    status: "Needs primary source",
    source:
      "Voice of Nigeria: Vice Chancellor commends President Buhari's efforts to improve healthcare delivery",
    sourceUrl:
      "https://von.gov.ng/vice-chancellor-commends-president-buharis-efforts-to-improve-healthcare-delivery/",
  },
  {
    id: "EK-033",
    date: "18–19 Jun 2022",
    title: "Oyebanji declared winner of 2022 governorship election",
    description:
      "The governorship election was held on 18 June 2022. In INEC's declaration of result, Biodun Oyebanji (APC) was declared elected with 187,057 votes, ahead of Segun Oni (SDP) with 82,211 and Bisi Kolawole (PDP) with 67,457.",
    category: "Government",
    status: "Verified",
    source: "INEC (official Facebook page): Declaration of Result, Ekiti State Governorship Election",
    sourceUrl:
      "https://www.facebook.com/inecnigeria/posts/declaration-of-result-of-the-ekiti-state-governorship-election-held-on-saturday-/404942308325501/",
  },
  {
    id: "EK-032",
    date: "Aug 2022",
    title: "MICS6 results show Ekiti with second-lowest out-of-school rate",
    description:
      "Results of the Multiple Indicator Cluster Survey 6, presented by a UNICEF official in August 2022, are reported to put Ekiti's out-of-school rate at 2 percent, second only to Imo at 1 percent.",
    category: "Education",
    status: "Needs primary source",
    source: "Prime Business Africa: Imo, Ekiti Record Lowest Number Of Out Of School Children",
    sourceUrl:
      "https://www.primebusiness.africa/imo-ekiti-record-lowest-number-of-out-of-school-children-surveys",
  },
  {
    id: "EK-035",
    date: "Oct 2022 (year disputed)",
    title: "Ekiti airport ceremonially commissioned while unfinished",
    description:
      "Governor Fayemi commissioned the airport in a ceremony shortly before leaving office; the state government of the day said the facility was still under construction.",
    category: "Infrastructure",
    status: "Conflicting sources",
    source: "SaharaReporters: Ekiti Government confirms airport still under construction (22 Oct 2022)",
    sourceUrl:
      "https://saharareporters.com/2022/10/22/ekiti-government-confirms-saharareporters-story-says-cargo-airport-commissioned-ex",
  },
  {
    id: "EK-034",
    date: "16 Oct 2022",
    title: "Oyebanji sworn in as governor",
    description:
      "Biodun Oyebanji was sworn in as governor of Ekiti State on Sunday 16 October 2022, succeeding Kayode Fayemi.",
    category: "Government",
    status: "Verified",
    source:
      "Ekiti State Government: Governor Oyebanji: My Vision is for Ekiti to be a Land of Prosperity",
    sourceUrl: "https://www.ekitistate.gov.ng/archives/24343",
  },
  {
    id: "EK-039",
    date: "2024 (late Aug or early Sep)",
    title: "Udiroko festival 2024: senators donate N110 million to Ado-Ekiti",
    description:
      "At the 2024 Udiroko festival in Ado-Ekiti, Senate leaders donated N110 million toward the town's development and Senate President Akpabio was installed as an honorary chief.",
    category: "Culture",
    status: "Single source",
    source: "Tribune Online: Udiroko festival 2024",
    sourceUrl:
      "https://tribuneonlineng.com/udiroko-festival-celebrating-culture-tradition-towards-devpt-of-ado-ekiti/",
  },
  {
    id: "EK-048",
    date: "Feb 2024",
    title: "Ekiti partners Agbeyewa Farms on cassava investment",
    description:
      "The state government announced a partnership with Agbeyewa Farms, a Cavista Holdings subsidiary, starting with a 100-hectare cassava plantation at Ipao-Ekiti, Ikole LGA.",
    category: "Agriculture",
    status: "Single source",
    source: "THISDAY: Agbeyewa Farm Set to Enhance Food Security, Create Jobs in Ekiti",
    sourceUrl:
      "https://www.thisdaylive.com/2024/02/23/agbeyewa-farm-set-to-enhance-food-security-create-jobs-in-ekiti/",
  },
  {
    id: "EK-038",
    date: "22 Feb 2024",
    title: "African Development Bank announces $80 million for Ekiti Knowledge Zone",
    description:
      "The African Development Bank announced an $80 million commitment to the Ekiti Knowledge Zone project, including a 20-hectare green technology park and ICT training for over 19,000 young people.",
    category: "Technology",
    status: "Verified",
    source: "African Development Bank press release",
    sourceUrl:
      "https://www.afdb.org/en/news-and-events/press-releases/catalyzing-digital-innovation-african-development-bank-commits-80-million-ekiti-knowledge-zone-project-nigeria-68862",
  },
  {
    id: "EK-040",
    date: "Oct 2024 (day differs)",
    title: "80-bed multipurpose hospital complex flagged off at EKSUTH",
    description:
      "Governor Oyebanji flagged off construction of an 80-bed multipurpose medical building at the Ekiti State University Teaching Hospital, Ado-Ekiti, in October 2024.",
    category: "Health",
    status: "Verified",
    source: "Ekiti State Government: Gov. Oyebanji Flags Off Multipurpose 80 Bed Hospital Facility",
    sourceUrl: "https://www.ekitistate.gov.ng/?p=29579",
  },
  {
    id: "EK-049",
    date: "May 2025",
    title: "Ekiti receives National Sports Festival torch; sports complex and stadium works under way",
    description:
      "Ekiti received the torch of unity for the Ogun 2025 National Sports Festival. The state said it was building a 900-seat indoor sports complex and renovating the Oluyemi Kayode Stadium in Ado-Ekiti.",
    category: "Sports",
    status: "Single source",
    source: "Ekiti State Government: Ekiti Receives Ogun 2025 National Sports Festival Torch Of Unity",
    sourceUrl: "https://www.ekitistate.gov.ng/archives/30921",
  },
  {
    id: "EK-041",
    date: "Oct 2025",
    title: "NCAA approves commercial operations at Ekiti airport",
    description:
      "The Nigerian Civil Aviation Authority granted a six-month approval for commercial operations at the Ado-Ekiti airport in early October 2025.",
    category: "Infrastructure",
    status: "Verified",
    source: "ch-aviation: Ado Ekiti opens for first commercial flights",
    sourceUrl:
      "https://www.ch-aviation.com/news/161786-ado-ekiti-nigeria-opens-for-first-commercial-flights",
  },
  {
    id: "EK-050",
    date: "19–23 Nov 2025",
    title: "Ewi of Ado-Ekiti marks 35th coronation anniversary and 80th birthday",
    description:
      "Oba Rufus Adejugbe Aladesanmi III, the Ewi of Ado-Ekiti, celebrated 35 years on the throne and his 80th birthday with a five-day programme.",
    category: "Culture",
    status: "Verified",
    source:
      "Ekiti State Government: Gov. Oyebanji Congratulates Ewi Of Ado Ekiti On 80th Birthday, 35th Coronation Anniversary",
    sourceUrl: "https://www.ekitistate.gov.ng/archives/32102",
  },
  {
    id: "EK-042",
    date: "10 Dec 2025",
    title: "First commercial flight lands at Ekiti Agro-Allied International Cargo Airport",
    description:
      "United Nigeria Airlines operated the first commercial flight to the airport, connecting Ado-Ekiti with Abuja and Lagos.",
    category: "Infrastructure",
    status: "Verified",
    source: "TheCable: Ekiti airport begins commercial flight operations",
    sourceUrl: "https://www.thecable.ng/ekiti-airport-begins-commercial-flight-operations/",
  },
  {
    id: "EK-043",
    date: "9 Jun 2026",
    title: "Sod turned for Ekiti Knowledge Zone",
    description:
      "Vice President Kashim Shettima, representing President Tinubu, turned the sod for the Ekiti Knowledge Zone at Ago Araromi, Ado-Ekiti, on Tuesday 9 June 2026.",
    category: "Technology",
    status: "Verified",
    source:
      "Ekiti State Government: Ekiti Knowledge Zone 'll Be Nigeria's Innovation, Job Creation Hub",
    sourceUrl: "https://www.ekitistate.gov.ng/archives/33184",
  },
  {
    id: "EK-044",
    date: "20–21 Jun 2026",
    title: "Oyebanji declared winner of governorship election",
    description:
      "The governorship election was held on 20 June 2026. At about 3:13 a.m. on Sunday 21 June, INEC's State Returning Officer declared Biodun Oyebanji (APC) the winner with 319,224 votes, against 40,543 for Wole Oluyede (PDP) and 12,872 for Dare Bejide (ADC).",
    category: "Government",
    status: "Needs primary source",
    source:
      "Channels TV: INEC declares APC's Oyebanji winner of Ekiti governorship election",
    sourceUrl:
      "https://www.channelstv.com/2026/06/21/inec-declares-apcs-oyebanji-winner-of-ekiti-gov-election/",
  },
  {
    id: "EK-045",
    date: "2026 (Aug)",
    title: "Udiroko festival 2026 celebrated in Ado-Ekiti",
    description: "Ado-Ekiti celebrated the Udiroko festival in August 2026.",
    category: "Culture",
    status: "Single source",
    source: "Channels TV: Ado-Ekiti celebrates Udiroko Festival (21 Aug 2026)",
    sourceUrl:
      "https://www.channelstv.com/2026/08/21/heritage-unity-progress-on-display-as-ado-ekiti-celebrates-udiroko-festival/",
  },
];
