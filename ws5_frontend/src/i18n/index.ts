import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./en.json";

void i18n.use(initReactI18next).init({
  resources: { en: { translation: en } },
  lng: "en",
  supportedLngs: ["en"],
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

i18n.on("languageChanged", () => {
  if (typeof document !== "undefined") document.documentElement.lang = "en";
});

export default i18n;
