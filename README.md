# Food Nutrition Comparison (India)

## Product Specs
 
The product specifications and data schema are maintained in `Product_Specs.docx` in this repository. Please refer to this file for the latest fields and structure. It will be updated as the project evolves. 

## Cloud Data Hosting (Firebase)

We host the canonical CSV at `public/products.csv` via Firebase Hosting. Deploys are automated with GitHub Actions. The Android app fetches the CSV from the live Hosting URL (e.g., `https://<project-id>.web.app/products.csv`) only when the user requests a refresh.

- Update data: modify `data/products.csv`, then copy to `public/products.csv` and push to `main`.
- Deployment: GitHub Actions deploys to Firebase Hosting on each push to `main`.
- Access in app: configure the app to download the CSV from the live Hosting URL. 