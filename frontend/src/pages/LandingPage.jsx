/**
 * LandingPage Component
 * Main landing page assembling all sections
 */
import Navbar from '../components/landing/Navbar';
import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import HowItWorks from '../components/landing/HowItWorks';
import Pricing from '../components/landing/Pricing';
import Footer from '../components/landing/Footer';
import SEO from '../components/SEO';

export default function LandingPage() {
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "ImmoSafe DE - Naturkatastrophen-Risikoanalyse",
    "applicationCategory": "BusinessApplication",
    "description": "Professionelle Risikoanalyse für deutsche Immobilien. Analyse von Hochwasser, Sturm, Waldbrand, Erdbeben und mehr mit konkreten Handlungsempfehlungen.",
    "operatingSystem": "Web Browser",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "EUR",
      "availability": "https://schema.org/InStock"
    },
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.8",
      "ratingCount": "127",
      "bestRating": "5",
      "worstRating": "1"
    },
    "featureList": [
      "Hochwasseranalyse mit historischen Niederschlagsdaten",
      "Sturmrisikoanalyse mit Windgeschwindigkeiten",
      "Waldbrandanalyse mit Temperatur- und Trockenheitsindex",
      "Erdbebenanalyse nach DIN EN 1998-1",
      "Versicherungsempfehlungen mit Kosteneinschätzungen",
      "Regionaler Vergleich mit Bundesland-Benchmarks",
      "Priorisierter Maßnahmenplan mit ROI-Berechnungen",
      "Professioneller PDF-Bericht zum Download"
    ],
    "author": {
      "@type": "Organization",
      "name": "ImmoSafe DE"
    },
    "datePublished": "2024-01-12",
    "inLanguage": "de-DE"
  };

  return (
    <>
      <SEO
        title="ImmoSafe DE - Naturkatastrophen-Risikoanalyse für deutsche Immobilien"
        description="Schützen Sie Ihre Immobilie! Professionelle Analyse von Hochwasser, Sturm, Waldbrand & Erdbeben. Versicherungsempfehlungen, Handlungsplan & regionaler Vergleich. Jetzt kostenlos testen!"
        keywords="Immobilien Risikoanalyse Deutschland, Hochwasserrisiko prüfen, Naturkatastrophen Immobilie, Elementarversicherung Empfehlung, Immobilienbewertung Klimarisiko, Gebäudeversicherung Vergleich, Erdbebenzone Deutschland, Sturmschaden Immobilie, Waldbrandgefahr Deutschland"
        structuredData={structuredData}
      />
      <div className="min-h-screen bg-white">
        <Navbar />
        <main>
          <Hero />
          <Features />
          <HowItWorks />
          <Pricing />
        </main>
        <Footer />
      </div>
    </>
  );
}
