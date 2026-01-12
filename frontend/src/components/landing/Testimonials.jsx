/**
 * Testimonials Component
 * Social proof section with customer testimonials and stats
 */
import { motion } from 'framer-motion';
import { Star, Quote, TrendingUp, Users, MapPin } from 'lucide-react';

export default function Testimonials() {
  const testimonials = [
    {
      quote: 'ImmoSafe hat uns vor einem teuren Fehler bewahrt. Das Grundstück lag in einer Senke, die wir auf den ersten Blick nicht erkannt hatten.',
      author: 'Thomas M.',
      role: 'Immobilienkäufer, München',
      rating: 5,
    },
    {
      quote: 'Als Makler nutze ich ImmoSafe bei jeder Objektbesichtigung. Die Kunden schätzen die professionelle Risikoeinschätzung.',
      author: 'Sandra K.',
      role: 'Immobilienmaklerin, Hamburg',
      rating: 5,
    },
    {
      quote: 'Schnell, präzise und verständlich. Der PDF-Bericht ist perfekt für unsere Finanzierungsunterlagen.',
      author: 'Michael R.',
      role: 'Bauherr, Berlin',
      rating: 5,
    },
  ];

  const stats = [
    { value: '10.000+', label: 'Analysen durchgeführt', icon: TrendingUp },
    { value: '2.500+', label: 'Zufriedene Nutzer', icon: Users },
    { value: '16', label: 'Bundesländer abgedeckt', icon: MapPin },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
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
    <section className="py-24 bg-white relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-white via-slate-50/50 to-white" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
          className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-3xl p-8 mb-20 shadow-2xl shadow-primary-500/20"
        >
          <div className="grid md:grid-cols-3 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div
                  key={index}
                  className="text-center md:text-left flex flex-col md:flex-row items-center md:items-start space-y-3 md:space-y-0 md:space-x-4"
                >
                  <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-3xl font-bold text-white">{stat.value}</p>
                    <p className="text-primary-100 text-sm font-medium">{stat.label}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>

        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 bg-amber-50 text-amber-700 text-sm font-semibold rounded-full mb-4">
            Kundenstimmen
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            Was unsere{' '}
            <span className="bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent">
              Nutzer
            </span>{' '}
            sagen
          </h2>
        </motion.div>

        {/* Testimonials Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
          className="grid md:grid-cols-3 gap-6"
        >
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="relative bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-lg transition-shadow duration-300"
            >
              {/* Quote Icon */}
              <div className="absolute -top-3 -left-3 w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center shadow-lg">
                <Quote className="w-5 h-5 text-white" />
              </div>

              {/* Stars */}
              <div className="flex space-x-1 mb-4 pt-2">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
                ))}
              </div>

              {/* Quote */}
              <p className="text-slate-700 leading-relaxed mb-6 italic">
                "{testimonial.quote}"
              </p>

              {/* Author */}
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-slate-200 to-slate-300 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold text-slate-600">
                    {testimonial.author.charAt(0)}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">{testimonial.author}</p>
                  <p className="text-xs text-slate-500">{testimonial.role}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
