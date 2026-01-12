/**
 * Features Component
 * Showcase of key product features with icons and descriptions
 */
import { motion } from 'framer-motion';
import { Mountain, CloudRain, History, FileText, Zap, Shield } from 'lucide-react';

export default function Features() {
  const features = [
    {
      icon: Mountain,
      title: 'Höhenanalyse',
      description: 'Präzise Geländeanalyse basierend auf offiziellen Höhendaten. Erkennung von Tal- und Senkenlagen.',
      color: 'from-slate-500 to-slate-700',
      bgColor: 'bg-slate-100',
    },
    {
      icon: CloudRain,
      title: 'Wetterprognose',
      description: '3-Tage Wettervorhersage mit Niederschlagsmengen vom Deutschen Wetterdienst.',
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-100',
    },
    {
      icon: History,
      title: 'Historische Daten',
      description: 'Analyse der Niederschläge der letzten 7 Tage für ein vollständiges Risikobild.',
      color: 'from-amber-500 to-orange-500',
      bgColor: 'bg-amber-100',
    },
    {
      icon: FileText,
      title: 'PDF-Bericht',
      description: 'Professioneller Risikobericht zum Download. Ideal für Immobilienkäufe und Versicherungen.',
      color: 'from-emerald-500 to-teal-500',
      bgColor: 'bg-emerald-100',
    },
    {
      icon: Zap,
      title: 'Sofort-Ergebnis',
      description: 'Erhalten Sie Ihre Risikoanalyse in Sekunden. Keine Wartezeit, keine Anmeldung nötig.',
      color: 'from-violet-500 to-purple-500',
      bgColor: 'bg-violet-100',
    },
    {
      icon: Shield,
      title: 'Zuverlässige Daten',
      description: 'Basierend auf offiziellen deutschen Wetterdiensten und Geodaten-Anbietern.',
      color: 'from-rose-500 to-pink-500',
      bgColor: 'bg-rose-100',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: 'easeOut',
      },
    },
  };

  return (
    <section id="features" className="py-24 bg-white relative overflow-hidden">
      {/* Background Decoration */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-gradient-to-b from-primary-50/50 to-transparent rounded-full blur-3xl" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 bg-primary-50 text-primary-700 text-sm font-semibold rounded-full mb-4">
            Features
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            Alles was Sie für eine{' '}
            <span className="bg-gradient-to-r from-primary-600 to-cyan-500 bg-clip-text text-transparent">
              fundierte Entscheidung
            </span>{' '}
            brauchen
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            ImmoSafe kombiniert verschiedene Datenquellen zu einer umfassenden 
            Hochwasser-Risikoanalyse für jede deutsche Adresse.
          </p>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                variants={itemVariants}
                className="group relative bg-white rounded-2xl p-6 border border-slate-200 hover:border-slate-300 shadow-sm hover:shadow-xl transition-all duration-300"
              >
                {/* Icon */}
                <div className={`w-14 h-14 ${feature.bgColor} rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className={`w-7 h-7 bg-gradient-to-r ${feature.color} bg-clip-text`} style={{ color: 'inherit' }} />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-slate-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-slate-600 leading-relaxed">
                  {feature.description}
                </p>

                {/* Hover Gradient */}
                <div className={`absolute inset-0 bg-gradient-to-r ${feature.color} opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity duration-300`} />
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
