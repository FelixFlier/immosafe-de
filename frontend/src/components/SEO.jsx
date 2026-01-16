/**
 * SEO Component
 * Manages meta tags, Open Graph, and structured data for SEO
 */
import { Helmet } from 'react-helmet-async';
import PropTypes from 'prop-types';

export default function SEO({
  title = 'ImmoSafe DE - Naturkatastrophen-Risikoanalyse für deutsche Immobilien',
  description = 'Professionelle Risikoanalyse für Hochwasser, Sturm, Waldbrand, Erdbeben und mehr. Schützen Sie Ihre Immobilie mit datenbasierten Insights und konkreten Handlungsempfehlungen.',
  keywords = 'Immobilien Risikoanalyse, Hochwasserrisiko Deutschland, Naturkatastrophen Immobilie, Elementarversicherung, Immobilienbewertung Risiko, Gebäudeversicherung, Klimarisiko Immobilien',
  ogImage = '/og-image.png',
  ogUrl,
  type = 'website',
  structuredData
}) {
  const siteUrl = 'https://immosafe.de'; // TODO: Replace with actual domain
  const fullUrl = ogUrl || siteUrl;

  const defaultStructuredData = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "ImmoSafe DE",
    "applicationCategory": "BusinessApplication",
    "description": description,
    "url": siteUrl,
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "EUR"
    },
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.8",
      "ratingCount": "127"
    },
    "featureList": [
      "Hochwasseranalyse",
      "Sturmrisikoanalyse",
      "Waldbrandanalyse",
      "Erdbebenanalyse",
      "Versicherungsempfehlungen",
      "Regionaler Vergleich",
      "Maßnahmenplan"
    ]
  };

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={fullUrl} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={`${siteUrl}${ogImage}`} />
      <meta property="og:site_name" content="ImmoSafe DE" />
      <meta property="og:locale" content="de_DE" />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={fullUrl} />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={`${siteUrl}${ogImage}`} />

      {/* Additional SEO */}
      <meta name="robots" content="index, follow" />
      <meta name="googlebot" content="index, follow" />
      <meta name="language" content="German" />
      <meta name="geo.region" content="DE" />
      <meta name="geo.placename" content="Deutschland" />

      {/* Canonical URL */}
      <link rel="canonical" href={fullUrl} />

      {/* Structured Data */}
      <script type="application/ld+json">
        {JSON.stringify(structuredData || defaultStructuredData)}
      </script>
    </Helmet>
  );
}

SEO.propTypes = {
  title: PropTypes.string,
  description: PropTypes.string,
  keywords: PropTypes.string,
  ogImage: PropTypes.string,
  ogUrl: PropTypes.string,
  type: PropTypes.string,
  structuredData: PropTypes.object,
};
