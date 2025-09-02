'use client';

import { useState } from 'react';
import { Search, Hospital, Shield, Pill, TrendingUp, MapPin, DollarSign } from 'lucide-react';
import { motion } from 'framer-motion';

export default function HomePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedService, setSelectedService] = useState('procedures');

  const services = [
    {
      id: 'procedures',
      title: 'Hospital Price Transparency',
      description: 'Compare procedure costs across Illinois hospitals',
      icon: Hospital,
      color: 'bg-blue-500',
      features: [
        'Real-time pricing data',
        'Procedure cost comparison',
        'Insurance vs. cash pricing',
        'Chicago metro area coverage'
      ]
    },
    {
      id: 'insurance',
      title: 'Insurance Navigation',
      description: 'AI-powered claim analysis and appeal assistance',
      icon: Shield,
      color: 'bg-green-500',
      features: [
        'Claim overcharge detection',
        'Automated appeal generation',
        'Insurance network analysis',
        'Cost optimization recommendations'
      ]
    },
    {
      id: 'medications',
      title: 'Medication Cost Optimization',
      description: 'Find the lowest-cost prescription options',
      icon: Pill,
      color: 'bg-purple-500',
      features: [
        'Pharmacy price comparison',
        'Generic alternatives',
        'Discount program matching',
        'Illinois pharmacy network'
      ]
    },
    {
      id: 'analytics',
      title: 'Healthcare Analytics',
      description: 'Data-driven insights and cost trends',
      icon: TrendingUp,
      color: 'bg-orange-500',
      features: [
        'Price anomaly detection',
        'Regional cost analysis',
        'Healthcare spending insights',
        'Predictive cost modeling'
      ]
    }
  ];

  const illinoisStats = [
    { label: 'Hospitals Covered', value: '15+', icon: Hospital },
    { label: 'Procedures Tracked', value: '10,000+', icon: TrendingUp },
    { label: 'Cities in Illinois', value: '25+', icon: MapPin },
    { label: 'Avg. Cost Savings', value: '$2,500+', icon: DollarSign }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-5xl md:text-6xl font-bold text-gray-900 mb-6"
            >
              Healthcare Transparency
              <span className="text-blue-600 block">Made Simple</span>
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto"
            >
              AI-powered healthcare cost optimization and transparency platform. 
              Starting with Illinois hospitals to help you make informed healthcare decisions.
            </motion.p>

            {/* Search Bar */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="max-w-2xl mx-auto mb-12"
            >
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="text"
                  placeholder="Search for procedures, hospitals, or medications..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 text-lg border-2 border-gray-200 rounded-full focus:border-blue-500 focus:outline-none shadow-lg"
                />
                <button className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white px-6 py-2 rounded-full hover:bg-blue-700 transition-colors">
                  Search
                </button>
              </div>
            </motion.div>

            {/* Illinois Focus Badge */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="inline-flex items-center px-6 py-3 bg-blue-100 text-blue-800 rounded-full font-semibold"
            >
              <MapPin className="h-5 w-5 mr-2" />
              Starting with Illinois • Chicago Metro Area
            </motion.div>
          </div>
        </div>
      </section>

      {/* Illinois Statistics */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Illinois Healthcare Coverage
            </h2>
            <p className="text-lg text-gray-600">
              Comprehensive data from hospitals across the state
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {illinoisStats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.1 * index }}
                className="text-center"
              >
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                  <stat.icon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Our Services
            </h2>
            <p className="text-lg text-gray-600">
              Comprehensive healthcare transparency and optimization tools
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {services.map((service, index) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.1 * index }}
                className={`bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow cursor-pointer ${
                  selectedService === service.id ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setSelectedService(service.id)}
              >
                <div className={`inline-flex items-center justify-center w-16 h-16 ${service.color} rounded-full mb-6`}>
                  <service.icon className="h-8 w-8 text-white" />
                </div>
                
                <h3 className="text-2xl font-bold text-gray-900 mb-4">{service.title}</h3>
                <p className="text-gray-600 mb-6">{service.description}</p>
                
                <ul className="space-y-3">
                  {service.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center text-sm text-gray-600">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                      {feature}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Take Control of Your Healthcare Costs?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of Illinois residents who are already saving money on healthcare
          </p>
          <div className="space-x-4">
            <button className="bg-white text-blue-600 px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors">
              Get Started
            </button>
            <button className="border-2 border-white text-white px-8 py-3 rounded-full font-semibold hover:bg-white hover:text-blue-600 transition-colors">
              Learn More
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
