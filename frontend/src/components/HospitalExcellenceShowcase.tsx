'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Award, 
  Star, 
  TrendingUp, 
  Users, 
  Heart, 
  Shield, 
  MapPin,
  Building,
  Trophy,
  Medal
} from 'lucide-react';

interface HospitalExcellence {
  id: number;
  hospital_id: number;
  category: string;
  title: string;
  description: string;
  transparency_score: number;
  community_impact_score: number;
  cost_effectiveness_score: number;
  patient_satisfaction_score: number;
  is_featured: boolean;
  is_spotlight: boolean;
  achievements: string;
  community_impact_details: string;
  cost_optimization_details: string;
  hospital: {
    id: number;
    name: string;
    city: string;
    county: string;
    bed_count: number;
    hospital_type: string;
  };
}

interface SmallHospitalExcellence {
  hospital: {
    id: number;
    name: string;
    city: string;
    bed_count: number;
    hospital_type: string;
  };
  transparency_score: number;
  community_impact_score: number;
  cost_effectiveness: number;
  excellence_recognition: string | null;
  is_featured: boolean;
  is_spotlight: boolean;
}

interface RuralHospitalHero {
  hospital: {
    id: number;
    name: string;
    city: string;
    county: string;
    bed_count: number;
    hospital_type: string;
  };
  transparency_score: number;
  community_impact_score: number;
  cost_effectiveness: number;
  rural_hero_qualities: string[];
}

export default function HospitalExcellenceShowcase() {
  const [featuredHospitals, setFeaturedHospitals] = useState<HospitalExcellence[]>([]);
  const [smallHospitals, setSmallHospitals] = useState<SmallHospitalExcellence[]>([]);
  const [ruralHeroes, setRuralHeroes] = useState<RuralHospitalHero[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'featured' | 'small' | 'rural'>('featured');

  useEffect(() => {
    fetchExcellenceData();
  }, []);

  const fetchExcellenceData = async () => {
    try {
      setLoading(true);
      
      // Fetch featured hospitals
      const featuredResponse = await fetch('/api/v1/hospital-excellence/excellence/featured?limit=6');
      const featuredData = await featuredResponse.json();
      setFeaturedHospitals(featuredData);

      // Fetch small hospital excellence
      const smallResponse = await fetch('/api/v1/hospital-excellence/small-hospitals/excellence?limit=6');
      const smallData = await smallResponse.json();
      setSmallHospitals(smallData.small_hospitals || []);

      // Fetch rural hospital heroes
      const ruralResponse = await fetch('/api/v1/hospital-excellence/rural-hospitals/heroes?limit=6');
      const ruralData = await ruralResponse.json();
      setRuralHeroes(ruralData.rural_heroes || []);

    } catch (error) {
      console.error('Error fetching excellence data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'small_hospital_excellence':
        return <Building className="h-6 w-6" />;
      case 'rural_innovation':
        return <MapPin className="h-6 w-6" />;
      case 'community_focus':
        return <Heart className="h-6 w-6" />;
      case 'critical_access_excellence':
        return <Shield className="h-6 w-6" />;
      case 'community_partnership':
        return <Users className="h-6 w-6" />;
      default:
        return <Award className="h-6 w-6" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'small_hospital_excellence':
        return 'bg-blue-500';
      case 'rural_innovation':
        return 'bg-green-500';
      case 'community_focus':
        return 'bg-pink-500';
      case 'critical_access_excellence':
        return 'bg-purple-500';
      case 'community_partnership':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const FeaturedHospitalCard = ({ hospital }: { hospital: HospitalExcellence }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow p-6 border border-gray-100"
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`inline-flex items-center justify-center w-12 h-12 ${getCategoryColor(hospital.category)} rounded-full text-white mb-3`}>
          {getCategoryIcon(hospital.category)}
        </div>
        {hospital.is_spotlight && (
          <div className="flex items-center text-yellow-500">
            <Star className="h-5 w-5 fill-current" />
          </div>
        )}
      </div>

      <h3 className="text-xl font-bold text-gray-900 mb-2">{hospital.hospital.name}</h3>
      <p className="text-gray-600 mb-3">{hospital.hospital.city}, {hospital.hospital.county}</p>
      
      <div className="mb-4">
        <h4 className="font-semibold text-gray-800 mb-2">{hospital.title}</h4>
        <p className="text-sm text-gray-600">{hospital.description}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <div className={`text-2xl font-bold ${getScoreColor(hospital.transparency_score)}`}>
            {hospital.transparency_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">Transparency</div>
        </div>
        <div className="text-center">
          <div className={`text-2xl font-bold ${getScoreColor(hospital.community_impact_score)}`}>
            {hospital.community_impact_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">Community Impact</div>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-500">{hospital.hospital.bed_count} beds</span>
        <span className="text-gray-500">{hospital.hospital.hospital_type}</span>
      </div>
    </motion.div>
  );

  const SmallHospitalCard = ({ hospital }: { hospital: SmallHospitalExcellence }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow p-6 border border-gray-100"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-500 rounded-full text-white mb-3">
          <Building className="h-6 w-6" />
        </div>
        {hospital.is_featured && (
          <div className="flex items-center text-blue-500">
            <Trophy className="h-5 w-5" />
          </div>
        )}
      </div>

      <h3 className="text-xl font-bold text-gray-900 mb-2">{hospital.hospital.name}</h3>
      <p className="text-gray-600 mb-3">{hospital.hospital.city}</p>
      
      {hospital.excellence_recognition && (
        <div className="mb-4">
          <h4 className="font-semibold text-blue-600 mb-2">{hospital.excellence_recognition}</h4>
          <p className="text-sm text-gray-600">Small Hospital Excellence Award</p>
        </div>
      )}

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className={`text-lg font-bold ${getScoreColor(hospital.transparency_score)}`}>
            {hospital.transparency_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">Transparency</div>
        </div>
        <div className="text-center">
          <div className={`text-lg font-bold ${getScoreColor(hospital.community_impact_score)}`}>
            {hospital.community_impact_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">Community</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-600">
            ${hospital.cost_effectiveness.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">Cost/Bed</div>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-500">{hospital.hospital.bed_count} beds</span>
        <span className="text-gray-500">{hospital.hospital.hospital_type}</span>
      </div>
    </motion.div>
  );

  const RuralHeroCard = ({ hero }: { hero: RuralHospitalHero }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow p-6 border border-gray-100"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-green-500 rounded-full text-white mb-3">
          <Heart className="h-6 w-6" />
        </div>
        <div className="flex items-center text-green-500">
          <Medal className="h-5 w-5" />
        </div>
      </div>

      <h3 className="text-xl font-bold text-gray-900 mb-2">{hero.hospital.name}</h3>
      <p className="text-gray-600 mb-3">{hero.hospital.city}, {hero.hospital.county}</p>
      
      <div className="mb-4">
        <h4 className="font-semibold text-green-600 mb-2">Rural Healthcare Hero</h4>
        <p className="text-sm text-gray-600">Essential community healthcare provider</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className={`text-lg font-bold ${getScoreColor(hero.transparency_score)}`}>
            {hero.transparency_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">Transparency</div>
        </div>
        <div className="text-center">
          <div className={`text-lg font-bold ${getScoreColor(hero.community_impact_score)}`}>
            {hero.community_impact_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">Community</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-600">
            ${hero.cost_effectiveness.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">Cost/Bed</div>
        </div>
      </div>

      <div className="mb-4">
        <h5 className="font-semibold text-gray-800 mb-2">Hero Qualities:</h5>
        <ul className="text-sm text-gray-600 space-y-1">
          {hero.rural_hero_qualities.map((quality, index) => (
            <li key={index} className="flex items-center">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></div>
              {quality}
            </li>
          ))}
        </ul>
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-500">{hero.hospital.bed_count} beds</span>
        <span className="text-gray-500">{hero.hospital.hospital_type}</span>
      </div>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading hospital excellence data...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-4xl font-bold text-gray-900 mb-4"
          >
            Illinois Healthcare Excellence
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-xl text-gray-600 max-w-3xl mx-auto"
          >
            Celebrating hospitals that demonstrate outstanding transparency, community impact, and cost-effective healthcare delivery
          </motion.p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-12">
          <div className="bg-white rounded-lg p-1 shadow-sm border border-gray-200">
            <button
              onClick={() => setActiveTab('featured')}
              className={`px-6 py-3 rounded-md font-medium transition-colors ${
                activeTab === 'featured'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Featured Excellence
            </button>
            <button
              onClick={() => setActiveTab('small')}
              className={`px-6 py-3 rounded-md font-medium transition-colors ${
                activeTab === 'small'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Small Hospital Leaders
            </button>
            <button
              onClick={() => setActiveTab('rural')}
              className={`px-6 py-3 rounded-md font-medium transition-colors ${
                activeTab === 'rural'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Rural Healthcare Heroes
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {activeTab === 'featured' && featuredHospitals.map((hospital) => (
            <FeaturedHospitalCard key={hospital.id} hospital={hospital} />
          ))}
          
          {activeTab === 'small' && smallHospitals.map((hospital, index) => (
            <SmallHospitalCard key={index} hospital={hospital} />
          ))}
          
          {activeTab === 'rural' && ruralHeroes.map((hero, index) => (
            <RuralHeroCard key={index} hero={hero} />
          ))}
        </div>

        {/* Call to Action */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-center mt-16"
        >
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Supporting Healthcare Excellence Across Illinois
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              We believe in recognizing and promoting hospitals that demonstrate exceptional commitment to transparency, 
              community impact, and cost-effective healthcare delivery. Our fair scoring system ensures that hospitals 
              of all sizes are evaluated appropriately.
            </p>
            <div className="flex justify-center space-x-4">
              <button className="bg-blue-600 text-white px-8 py-3 rounded-full font-semibold hover:bg-blue-700 transition-colors">
                View All Hospitals
              </button>
              <button className="border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-full font-semibold hover:bg-blue-50 transition-colors">
                Learn About Scoring
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
