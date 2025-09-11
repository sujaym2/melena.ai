'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  Shield, 
  Users,
  Building,
  MapPin,
  FileText,
  ExternalLink
} from 'lucide-react';

interface AccountabilityTier {
  id: number;
  hospital_id: number;
  tier: string;
  enforcement_level: string;
  compliance_timeline_days: number;
  support_level: string;
  tier_reason: string;
  size_factor: boolean;
  resource_factor: boolean;
  community_factor: boolean;
  compliance_rate: number;
  improvement_rate: number;
  support_utilization: number;
  hospital: {
    id: number;
    name: string;
    city: string;
    county: string;
    bed_count: number;
    hospital_type: string;
  };
}

interface TransparencyScore {
  id: number;
  hospital_id: number;
  hospital_size: string;
  overall_transparency_score: number;
  data_accessibility_score: number;
  data_completeness_score: number;
  data_accuracy_score: number;
  update_frequency_score: number;
  peer_group_rank: number;
  peer_group_percentile: number;
  cost_per_bed_transparency: number;
  community_impact_score: number;
  patient_satisfaction_score: number;
  hospital: {
    id: number;
    name: string;
    city: string;
    county: string;
    bed_count: number;
    hospital_type: string;
  };
}

export default function HospitalAccountabilityDashboard() {
  const [accountabilityTiers, setAccountabilityTiers] = useState<AccountabilityTier[]>([]);
  const [transparencyScores, setTransparencyScores] = useState<TransparencyScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<'all' | 'strict' | 'supportive' | 'educational'>('all');
  const [sortBy, setSortBy] = useState<'score' | 'compliance' | 'improvement'>('score');

  useEffect(() => {
    fetchAccountabilityData();
  }, []);

  const fetchAccountabilityData = async () => {
    try {
      setLoading(true);
      
      // Fetch accountability tiers
      const tiersResponse = await fetch('/api/v1/hospital-excellence/accountability-tiers');
      const tiersData = await tiersResponse.json();
      setAccountabilityTiers(tiersData);

      // Fetch transparency scores
      const scoresResponse = await fetch('/api/v1/hospital-excellence/transparency-scores?limit=50');
      const scoresData = await scoresResponse.json();
      setTransparencyScores(scoresData);

    } catch (error) {
      console.error('Error fetching accountability data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'strict':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'supportive':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'educational':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'strict':
        return <AlertTriangle className="h-4 w-4" />;
      case 'supportive':
        return <Clock className="h-4 w-4" />;
      case 'educational':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Shield className="h-4 w-4" />;
    }
  };

  const getEnforcementLevelColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'text-red-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredTiers = accountabilityTiers.filter(tier => 
    activeFilter === 'all' || tier.tier === activeFilter
  );

  const sortedTiers = [...filteredTiers].sort((a, b) => {
    switch (sortBy) {
      case 'score':
        const scoreA = transparencyScores.find(s => s.hospital_id === a.hospital_id)?.overall_transparency_score || 0;
        const scoreB = transparencyScores.find(s => s.hospital_id === b.hospital_id)?.overall_transparency_score || 0;
        return scoreB - scoreA;
      case 'compliance':
        return (b.compliance_rate || 0) - (a.compliance_rate || 0);
      case 'improvement':
        return (b.improvement_rate || 0) - (a.improvement_rate || 0);
      default:
        return 0;
    }
  });

  const AccountabilityCard = ({ tier }: { tier: AccountabilityTier }) => {
    const transparencyScore = transparencyScores.find(s => s.hospital_id === tier.hospital_id);
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow p-6 border border-gray-100"
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`inline-flex items-center justify-center w-10 h-10 rounded-full ${getTierColor(tier.tier)}`}>
              {getTierIcon(tier.tier)}
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">{tier.hospital.name}</h3>
              <p className="text-sm text-gray-600">{tier.hospital.city}, {tier.hospital.county}</p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-sm font-semibold ${getEnforcementLevelColor(tier.enforcement_level)}`}>
              {tier.enforcement_level.toUpperCase()} ENFORCEMENT
            </div>
            <div className="text-xs text-gray-500">{tier.compliance_timeline_days} days to comply</div>
          </div>
        </div>

        <div className="mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getTierColor(tier.tier)}`}>
              {tier.tier.toUpperCase()} TIER
            </span>
            <span className="text-xs text-gray-500">{tier.hospital.bed_count} beds</span>
          </div>
          <p className="text-sm text-gray-600">{tier.tier_reason}</p>
        </div>

        {transparencyScore && (
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center">
              <div className={`text-2xl font-bold ${getScoreColor(transparencyScore.overall_transparency_score)}`}>
                {transparencyScore.overall_transparency_score.toFixed(1)}
              </div>
              <div className="text-xs text-gray-500">Transparency Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {transparencyScore.peer_group_rank || 'N/A'}
              </div>
              <div className="text-xs text-gray-500">Peer Group Rank</div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">
              {tier.compliance_rate ? `${tier.compliance_rate.toFixed(1)}%` : 'N/A'}
            </div>
            <div className="text-xs text-gray-500">Compliance Rate</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-blue-600">
              {tier.improvement_rate ? `${tier.improvement_rate.toFixed(1)}%` : 'N/A'}
            </div>
            <div className="text-xs text-gray-500">Improvement Rate</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-purple-600">
              {tier.support_utilization ? `${tier.support_utilization.toFixed(1)}%` : 'N/A'}
            </div>
            <div className="text-xs text-gray-500">Support Usage</div>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            {tier.size_factor && <span>Size Factor</span>}
            {tier.resource_factor && <span>Resource Factor</span>}
            {tier.community_factor && <span>Community Factor</span>}
          </div>
          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
            View Details <ExternalLink className="h-3 w-3 inline ml-1" />
          </button>
        </div>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading accountability data...</p>
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
            Hospital Accountability Dashboard
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-xl text-gray-600 max-w-3xl mx-auto"
          >
            Fair and balanced accountability system that supports hospitals of all sizes while ensuring transparency compliance
          </motion.p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="bg-white rounded-xl shadow-lg p-6 text-center"
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mb-4">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {accountabilityTiers.filter(t => t.tier === 'strict').length}
            </div>
            <div className="text-sm text-gray-600">Strict Enforcement</div>
            <div className="text-xs text-gray-500 mt-1">Large Hospitals</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="bg-white rounded-xl shadow-lg p-6 text-center"
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-yellow-100 rounded-full mb-4">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {accountabilityTiers.filter(t => t.tier === 'supportive').length}
            </div>
            <div className="text-sm text-gray-600">Supportive Assistance</div>
            <div className="text-xs text-gray-500 mt-1">Medium Hospitals</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="bg-white rounded-xl shadow-lg p-6 text-center"
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-4">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {accountabilityTiers.filter(t => t.tier === 'educational').length}
            </div>
            <div className="text-sm text-gray-600">Educational Support</div>
            <div className="text-xs text-gray-500 mt-1">Small Hospitals</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="bg-white rounded-xl shadow-lg p-6 text-center"
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mb-4">
              <TrendingUp className="h-6 w-6 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {transparencyScores.length}
            </div>
            <div className="text-sm text-gray-600">Total Hospitals</div>
            <div className="text-xs text-gray-500 mt-1">Tracked</div>
          </motion.div>
        </div>

        {/* Filters and Controls */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-8 space-y-4 md:space-y-0">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeFilter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              All Tiers
            </button>
            <button
              onClick={() => setActiveFilter('strict')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeFilter === 'strict'
                  ? 'bg-red-600 text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              Strict
            </button>
            <button
              onClick={() => setActiveFilter('supportive')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeFilter === 'supportive'
                  ? 'bg-yellow-600 text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              Supportive
            </button>
            <button
              onClick={() => setActiveFilter('educational')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeFilter === 'educational'
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              Educational
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="score">Transparency Score</option>
              <option value="compliance">Compliance Rate</option>
              <option value="improvement">Improvement Rate</option>
            </select>
          </div>
        </div>

        {/* Hospital Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {sortedTiers.map((tier) => (
            <AccountabilityCard key={tier.id} tier={tier} />
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
              Fair and Balanced Accountability
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Our tiered accountability system ensures that hospitals of all sizes are treated fairly. 
              Large hospitals face strict enforcement, while small and rural hospitals receive educational 
              support and flexible timelines to achieve compliance.
            </p>
            <div className="flex justify-center space-x-4">
              <button className="bg-blue-600 text-white px-8 py-3 rounded-full font-semibold hover:bg-blue-700 transition-colors">
                View Methodology
              </button>
              <button className="border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-full font-semibold hover:bg-blue-50 transition-colors">
                Download Report
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
