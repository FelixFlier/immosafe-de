/**
 * HowItWorks Component
 * 3-step process explanation with visual timeline
 */
import { motion } from 'framer-motion';
import { MapPin, BarChart3, Download, ArrowRight } from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      number: '01',
      icon: MapPin,
      title: 'Adresse eingeben',
      description: 'Geben Sie eine beliebige deutsche Adresse ein. Unsere Google-Integration findet den genauen Standort.',
      color: 'from-primary-500 to-primary-700',
    },
    {
      number: '02',
      icon: BarChart3,
      title: 'Analyse erhalten',
      description: 'Innerhalb von Sekunden analysieren wir Höhenlage, Wetterverlauf und Prognosen für Ihr Grundstück.',
      color: 'from-cyan-500 to-blue-600',
    },
    {
      number: '03',
      icon: Download,
      title: 'Bericht herunterladen',
      description: 'Laden Sie einen professionellen PDF-Bericht herunter – perfekt für Immobilienentscheidungen.',
      color: 'from-emerald-500 to-teal-600',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 40 },
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
    <section id="how-it-works" className="py-24 bg-gradient-to-b from-slate-50 to-white relative overflow-hidden">
      {/* Background Decoration */}
      <div className="absolute top-1/2 left-0 w-[400px] h-[400px] bg-primary-100/30 rounded-full blur-3xl -translate-y-1/2" />
      <div className="absolute bottom-0 right-0 w-[300px] h-[300px] bg-cyan-100/30 rounded-full blur-3xl" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <span className="inline-block px-4 py-1.5 bg-cyan-50 text-cyan-700 text-sm font-semibold rounded-full mb-4">
            So funktioniert's
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            In 3 Schritten zur{' '}
            <span className="bg-gradient-to-r from-cyan-500 to-primary-600 bg-clip-text text-transparent">
              Risikoanalyse
            </span>
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Keine Anmeldung, keine Wartezeit. Starten Sie sofort mit Ihrer Analyse.
          </p>
        </motion.div>

        {/* Steps */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
          className="relative"
        >
          {/* Connection Line (Desktop) */}
          <div className="hidden lg:block absolute top-1/2 left-[16%] right-[16%] h-0.5 bg-gradient-to-r from-primary-200 via-cyan-200 to-emerald-200 -translate-y-1/2" />

          <div className="grid lg:grid-cols-3 gap-8 lg:gap-12">
            {steps.map((step, index) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={index}
                  variants={itemVariants}
                  className="relative"
                >
                  {/* Card */}
                  <div className="bg-white rounded-3xl p-8 shadow-xl shadow-slate-900/5 border border-slate-100 hover:border-slate-200 transition-all duration-300 group">
                    {/* Step Number */}
                    <div className="flex items-center justify-between mb-6">
                      <span className={`text-5xl font-black bg-gradient-to-r ${step.color} bg-clip-text text-transparent opacity-30 group-hover:opacity-50 transition-opacity`}>
                        {step.number}
                      </span>
                      
                      {/* Icon */}
                      <div className={`w-16 h-16 bg-gradient-to-r ${step.color} rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                    </div>

                    {/* Content */}
                    <h3 className="text-xl font-bold text-slate-900 mb-3">
                      {step.title}
                    </h3>
                    <p className="text-slate-600 leading-relaxed">
                      {step.description}
                    </p>
                  </div>

                  {/* Arrow (between cards on mobile) */}
                  {index < steps.length - 1 && (
                    <div className="lg:hidden flex justify-center my-4">
                      <ArrowRight className="w-6 h-6 text-slate-300 rotate-90" />
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
