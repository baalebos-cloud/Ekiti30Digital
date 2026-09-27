# EKITI@30 DIGITAL — Image & Media Specifications
**Maintained by:** Member 6 (UI/UX & Design Lead)  
**Target:** Members 4, 5, 7, and 8  

To prevent UI distortion, unexpected cropping, and layout shifts across all devices, please adhere to these aspect ratios, resolution standards, and storage rules when collecting media.

---

## 1. Storage & Delivery Architecture (Important)
* **Cloudinary (Production Media Layer):** 
  * Serves as the actual storage, CDN delivery, and optimization engine for all binary image and video files.
  * Direct high-resolution file uploads should be processed through the designated Cloudinary workflow coordinated by Engineering.
* **`16_Media/` + Project Database (Metadata & Verification Records):**
  * Tracks media metadata, verified sources, photographer credits, copyright/usage permissions, and verification status badges.
  * Do not upload heavy production video or raw image archives directly into Git repositories. Store their tracking records, captions, and Cloudinary URLs/IDs here.

---

## 2. Homepage (`/`)
* **Hero Polaroids / Accent Pins (`.board .polaroid`):**
  * Aspect Ratio: `4:3` or `1:1` (Square)
  * Min Dimensions: `800 x 600px` (or `600 x 600px`)
  * Target Content: Archival moments, state creation gazettes, iconic hilltops.
* **Leaders Strip (`LeadersStrip.tsx`):**
  * Aspect Ratio: `1:1` (Square portrait)
  * Min Dimensions: `400 x 400px`
  * Target Content: Official portraits of Military Administrators and Governors (1996–2026).
* **Landmarks Strip (`LandmarksStrip.tsx`):**
  * Aspect Ratio: `16:9` (Landscape)
  * Min Dimensions: `1200 x 675px`
  * Target Content: Ikogosi, Arinta, Fajuyi Memorial Park, rolling hills.

---

## 3. 30-Year Timeline (`/timeline`) — Member 4 (History)
* **Timeline Event Visuals:**
  * Aspect Ratio: `16:9` or `4:3`
  * Min Dimensions: `800 x 450px`
  * Target Content: News clippings, state gazettes, swearing-in ceremonies, infrastructure inaugurations.
  * *Note:* Historical black-and-white or lower-resolution archival scans are acceptable if verified.

---

## 4. Explore Ekiti (`/explore`) — Member 5 (Geospatial & LGAs)
* **LGA Header Cards / Landmark Thumbnails:**
  * Aspect Ratio: `16:9` (Card banner)
  * Min Dimensions: `640 x 360px`
  * Target Content: LGA secretariats, town halls, civic monuments.
* **GIS Map Markers / Popups:**
  * Aspect Ratio: `1:1` (Square thumbnail)
  * Min Dimensions: `300 x 300px`

---

## 5. Culture & Tourism — Member 7
* **Tourism Destination Hero / Cards:**
  * Aspect Ratio: `16:9` (Landscape) or `3:2`
  * Min Dimensions: `1200 x 800px`
  * Target Content: Natural reserves, waterfalls, festivals (Udiroko, Ogun), traditional crafts.

---

## 6. My Ekiti Story & Ekiti 2056 (`/my-story`, `/ekiti-2056`) — Member 8 (Community)
* **Citizen Story Attachments:**
  * Aspect Ratio: `4:3` or `16:9`
  * Min Dimensions: `800 x 600px`
* **Author / Contributor Portraits:**
  * Aspect Ratio: `1:1` (Square avatar)
  * Min Dimensions: `400 x 400px`
* **Vision 2056 Blueprint Media:**
  * Aspect Ratio: `16:9` (Infographics, architectural concepts, maps)
  * Min Dimensions: `1200 x 675px`

---

## 7. Submission & Naming Standards
1. **File Format:** Modern web formats (`.webp`, `.jpg`, `.jpeg`). Use `.png` only for seals or logos needing transparency.
2. **Naming Convention:** Lowercase with hyphens, indicating category and location:
   * `lga-ikere-olosunta-01.jpg`
   * `timeline-1996-state-creation.jpg`
   * `tourism-ikogosi-confluence.jpg`
