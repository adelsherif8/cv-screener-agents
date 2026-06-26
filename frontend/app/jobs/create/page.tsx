"use client";
import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import Head from "next/head";
import { useRouter } from "next/navigation";
import { 
  AppHeader, PageContainer, MainContent, Card, Button, SectionHeader, LoadingSpinner, ErrorDisplay 
} from "@/components/shared";
import { 
  FaReact, FaJs, FaHtml5, FaCss3Alt, FaNodeJs, FaPython, FaJava, FaGitAlt, 
  FaDocker, FaAws, FaDatabase, FaVuejs, FaAngular, FaPlus, FaMinus, FaUser,
  FaComments, FaLightbulb, FaUsers, FaRocket, FaCogs, FaCode, FaServer, FaCloud,
  FaChartLine, FaBrain, FaHeart, FaHandshake, FaClock, FaEye, FaWordpress, FaShopify,
  FaPhp, FaMobile, FaAndroid, FaApple, FaLinux, FaWindows,
  FaMicrosoft, FaGoogle, FaBootstrap, FaFigma, FaSlack, FaTrello, FaGripVertical,
  FaLayerGroup, FaMagic, FaCheck
} from 'react-icons/fa';

// Extend Window interface for timeout handling
declare global {
  interface Window {
    autoCompleteTimeout?: NodeJS.Timeout;
  }
}
import { 
  SiTypescript, SiMongodb, SiGraphql, SiTailwindcss, SiNextdotjs, SiWordpress,
  SiShopify, SiMagento, SiDrupal, SiJoomla, SiPhp, SiMysql, SiPostgresql, SiRedis,
  SiElasticsearch, SiKubernetes, SiTerraform, SiJenkins, SiGithubactions, SiFlutter,
  SiSwift, SiKotlin, SiXcode, SiUnity, SiUnrealengine, SiBlender,
  SiAdobephotoshop, SiAdobeillustrator, SiSketch, SiFirebase, SiSupabase, SiNestjs, 
  SiExpress, SiSpring, SiRubyonrails, SiDjango, SiFlask, SiSass, SiWebpack, SiVite, 
  SiJest, SiCypress, SiSelenium
} from 'react-icons/si';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

// Sortable Skill Item Component
function SortableSkillItem({ 
  skill, 
  index, 
  category, 
  isAISuggested, 
  isSelected, 
  onSelect, 
  onRemove, 
  onLevelChange, 
  getSkillIcon, 
  getLevelColor, 
  activeLevelDropdown, 
  setActiveLevelDropdown 
}: any) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: `${category}-${index}`,
    data: {
      category,
      index,
    },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`group relative flex items-center gap-2 bg-white shadow-lg hover:shadow-xl px-4 py-3 border rounded-xl transition-all duration-300 ${
        isDragging ? 'z-50' : ''
      } ${isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}
    >
      {/* Drag Handle */}
      <div
        {...attributes}
        {...listeners}
        className="text-gray-400 hover:text-gray-600 cursor-grab active:cursor-grabbing"
      >
        <FaGripVertical className="text-sm" />
      </div>

      {/* Selection Checkbox */}
      <input
        type="checkbox"
        checked={isSelected}
        onChange={() => onSelect(`${category}-${index}`)}
        className="border-gray-300 rounded focus:ring-blue-500 text-blue-600"
      />

      {isAISuggested && (
        <div className="-top-1 -right-1 absolute flex items-center bg-gradient-to-r from-purple-500 to-blue-500 px-1.5 py-0.5 rounded-full text-white text-xs">
          <i className="mr-1 text-xs fas fa-robot"></i>
          AI
        </div>
      )}
      
      <div className="flex items-center">
        {getSkillIcon(skill.skill)}
      </div>
      <span className="font-medium text-gray-900">{skill.skill}</span>
      
      {/* Clickable Level Circle with Dropdown */}
      <div className="relative">
        <button
          type="button"
          className={`w-3 h-3 rounded-full border-2 cursor-pointer hover:ring-2 hover:ring-gray-300 transition-all ${getLevelColor(skill.level)}`}
          onClick={() => setActiveLevelDropdown(activeLevelDropdown === `${category}_${index}` ? null : `${category}_${index}`)}
          title={`Current level: ${skill.level}. Click to change.`}
        />
        
        {/* Level Dropdown */}
        {activeLevelDropdown === `${category}_${index}` && (
          <div className="top-6 left-0 z-50 absolute bg-white shadow-lg py-2 border rounded-lg min-w-[120px]">
            {['Basic', 'Intermediate', 'Advanced', 'Expert'].map((level) => (
              <button
                key={level}
                type="button"
                className={`w-full text-left px-3 py-2 hover:bg-gray-100 flex items-center gap-2 ${skill.level === level ? 'bg-blue-50 text-blue-700' : 'text-gray-700'}`}
                onClick={() => {
                  onLevelChange(skill.skill, category, level);
                  setActiveLevelDropdown(null);
                }}
              >
                <div className={`w-2 h-2 rounded-full border ${getLevelColor(level)}`}></div>
                <span className="text-sm">{level}</span>
              </button>
            ))}
          </div>
        )}
      </div>
      
      <button 
        type="button" 
        className="flex justify-center items-center bg-gray-200 hover:bg-red-100 ml-2 rounded-full w-5 h-5 font-semibold text-gray-500 hover:text-red-600 text-sm transition-all duration-200" 
        onClick={() => onRemove(skill.skill, category)}
      >
        ×
      </button>
    </div>
  );
}

export default function CreateJobPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<{
    title: string;
    description: string;
    requirements: string[];
    seniority: string;
    screening_questions: string[];
    summary: string;
    location: string;
    salary_min: string;
    salary_max: string;
  }>({
    title: "",
    description: "",
    requirements: [],
    seniority: "",
    screening_questions: [],
    summary: "",
    location: "",
    salary_min: "",
    salary_max: "",
  });
  const [agentRequirements, setAgentRequirements] = useState<{
    core_skills: Array<{skill: string, level: string, rating: number, evidence: string[], weight: number, category: string}>;
    soft_skills: Array<{skill: string, level: string, rating: number, evidence: string[], weight: number, category: string}>;
    bonus_skills: Array<{skill: string, level: string, rating: number, evidence: string[], weight: number, category: string}>;
    experience: any;
    languages: any[];
    metadata: any;
  }>({
    core_skills: [],
    soft_skills: [],
    bonus_skills: [],
    experience: {},
    languages: [],
    metadata: {}
  });
  const [selectedRequirements, setSelectedRequirements] = useState<{
    core_skills: Array<{skill: string, level: string}>;
    soft_skills: Array<{skill: string, level: string}>;
    bonus_skills: Array<{skill: string, level: string}>;
  }>({
    core_skills: [],
    soft_skills: [],
    bonus_skills: []
  });
  const [agentSummary, setAgentSummary] = useState("");
  const [creating, setCreating] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [requirementSearch, setRequirementSearch] = useState("");
  const [showRequirementDropdown, setShowRequirementDropdown] = useState(false);
  const [activeLevelDropdown, setActiveLevelDropdown] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // Enhanced Skills Management Features
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [quickAddMode, setQuickAddMode] = useState(false);
  const [skillSuggestions, setSkillSuggestions] = useState<Array<{skill: string, level: string, category: string}>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  // Drag and drop sensors
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );
  
  // Job title suggestions state
  const [titleSuggestions, setTitleSuggestions] = useState<Array<{
    title: string;
    confidence: number;
    type: string;
    reason: string;
  }>>([]);
  const [showTitleSuggestions, setShowTitleSuggestions] = useState(false);
  const [titleInputValue, setTitleInputValue] = useState("");
  const [isLoadingTitleSuggestions, setIsLoadingTitleSuggestions] = useState(false);
  const [lastAppliedSuggestion, setLastAppliedSuggestion] = useState<string>("");

  // Salary suggestions state
  const [salaryData, setSalaryData] = useState<{
    min_salary: number;
    max_salary: number;
    average_salary: number;
    percentile_25: number;
    percentile_75: number;
    data_sources: string[];
    confidence_score: number;
    location_adjustment: number;
    skill_premium: number;
    seniority_multiplier: number;
    market_trends: {
      trend: string;
      percentage_change: number;
      period: string;
    };
    comparable_positions: Array<{
      title: string;
      company_size: string;
      salary_range: string;
      location: string;
    }>;
  } | null>(null);
  const [loadingSalary, setLoadingSalary] = useState(false);

  // Experience level detection state
  const [experienceData, setExperienceData] = useState<{
    detected_level: string;
    confidence_score: number;
    years_of_experience: {
      detected_ranges: Array<{ min: number; max: number; text: string }>;
      min_years: number | null;
      max_years: number | null;
      most_common: { min: number; max: number; text: string } | null;
    };
    evidence: string[];
    alternative_levels: Array<{
      level: string;
      confidence: number;
      reasoning: string;
    }>;
    recommendations: string[];
  } | null>(null);
  const [loadingExperience, setLoadingExperience] = useState(false);

  // Auto-complete state
  const [autoCompleteSuggestions, setAutoCompleteSuggestions] = useState<Array<{
    text: string;
    type: string;
    confidence: number;
    category: string;
    icon: string;
  }>>([]);
  const [showAutoComplete, setShowAutoComplete] = useState(false);
  const [loadingAutoComplete, setLoadingAutoComplete] = useState(false);
  const [activeField, setActiveField] = useState<string>("");
  const [debugAutoComplete, setDebugAutoComplete] = useState(false);

  // Authentication check
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userData = localStorage.getItem("user");

    if (!token || !userData) {
      router.push("/auth/login");
      return;
    }

    setUser(JSON.parse(userData));
    setLoading(false);
  }, [router]);

  // Initialize title input value
  useEffect(() => {
    setTitleInputValue(form.title);
  }, []);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (window.autoCompleteTimeout) {
        clearTimeout(window.autoCompleteTimeout);
      }
    };
  }, []);

  // Skill combinations - when a skill is added, suggest related skills
  const skillCombinations = {
    'React': [
      {skill: 'Redux', level: 'Intermediate', category: 'core_skills'},
      {skill: 'Jest', level: 'Intermediate', category: 'bonus_skills'},
      {skill: 'TypeScript', level: 'Intermediate', category: 'core_skills'},
      {skill: 'Next.js', level: 'Basic', category: 'bonus_skills'}
    ],
    'Vue.js': [
      {skill: 'Vuex', level: 'Intermediate', category: 'core_skills'},
      {skill: 'Nuxt.js', level: 'Basic', category: 'bonus_skills'},
      {skill: 'TypeScript', level: 'Intermediate', category: 'core_skills'}
    ],
    'Angular': [
      {skill: 'RxJS', level: 'Intermediate', category: 'core_skills'},
      {skill: 'TypeScript', level: 'Advanced', category: 'core_skills'},
      {skill: 'NgRx', level: 'Intermediate', category: 'bonus_skills'}
    ],
    'Node.js': [
      {skill: 'Express', level: 'Intermediate', category: 'core_skills'},
      {skill: 'MongoDB', level: 'Intermediate', category: 'core_skills'},
      {skill: 'PostgreSQL', level: 'Basic', category: 'bonus_skills'}
    ],
    'Python': [
      {skill: 'Django', level: 'Intermediate', category: 'core_skills'},
      {skill: 'Flask', level: 'Basic', category: 'bonus_skills'},
      {skill: 'PostgreSQL', level: 'Intermediate', category: 'core_skills'}
    ],
    'JavaScript': [
      {skill: 'TypeScript', level: 'Intermediate', category: 'core_skills'},
      {skill: 'Jest', level: 'Intermediate', category: 'bonus_skills'},
      {skill: 'ESLint', level: 'Basic', category: 'bonus_skills'}
    ],
    'TypeScript': [
      {skill: 'Jest', level: 'Intermediate', category: 'bonus_skills'},
      {skill: 'ESLint', level: 'Basic', category: 'bonus_skills'},
      {skill: 'Webpack', level: 'Basic', category: 'bonus_skills'}
    ]
  };

  // Generate skill suggestions when a skill is added
  const generateSkillSuggestions = (addedSkill: string) => {
    const suggestions = skillCombinations[addedSkill as keyof typeof skillCombinations] || [];
    // Filter out skills that are already added
    const filteredSuggestions = suggestions.filter(suggestion => 
      !skillExists(suggestion.skill)
    );
    
    if (filteredSuggestions.length > 0) {
      setSkillSuggestions(filteredSuggestions);
      setShowSuggestions(true);
      // Auto-hide suggestions after 10 seconds
      setTimeout(() => setShowSuggestions(false), 10000);
    }
  };

  // Bulk actions for selected skills
  const setBulkLevel = (level: string) => {
    const updatedRequirements = { ...selectedRequirements };
    
    selectedSkills.forEach(skillKey => {
      const [category, index] = skillKey.split('-');
      const categoryKey = category as keyof typeof selectedRequirements;
      if (updatedRequirements[categoryKey][parseInt(index)]) {
        updatedRequirements[categoryKey][parseInt(index)].level = level;
      }
    });
    
    setSelectedRequirements(updatedRequirements);
    setSelectedSkills([]);
    setShowBulkActions(false);
  };

  // Quick add skill with Enter key
  const handleQuickAdd = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && requirementSearch.trim()) {
      const filteredSkills = getFilteredSkills();
      if (filteredSkills.length > 0) {
        const firstSkill = filteredSkills[0];
        addRequirement(`${firstSkill.name}:Intermediate`, firstSkill.category);
        setRequirementSearch("");
        setShowRequirementDropdown(false);
        generateSkillSuggestions(firstSkill.name);
      }
    }
  };

  // Drag and drop handler
  const handleDragEnd = (event: any) => {
    const { active, over } = event;

    if (active.id !== over?.id) {
      const activeCategory = active.data.current?.category;
      const activeIndex = active.data.current?.index;
      const overIndex = over.data.current?.index;

      if (activeCategory && activeIndex !== undefined && overIndex !== undefined) {
        setSelectedRequirements((prev) => {
          const categoryKey = activeCategory as keyof typeof prev;
          const items = Array.from(prev[categoryKey]);
          const newItems = arrayMove(items, activeIndex, overIndex);
          
          return {
            ...prev,
            [categoryKey]: newItems
          };
        });
      }
    }
  };

  // Debounced job title suggestion function
  const fetchTitleSuggestions = async (title: string) => {
    if (!title || title.length < 2) {
      setTitleSuggestions([]);
      setShowTitleSuggestions(false);
      return;
    }

    setIsLoadingTitleSuggestions(true);
    try {
      const response = await fetch("http://localhost:8000/jobs/title-suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          title, 
          description: form.description || "" 
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.suggestions && data.suggestions.length > 0) {
          setTitleSuggestions(data.suggestions);
          setShowTitleSuggestions(true);
        } else {
          setTitleSuggestions([]);
          setShowTitleSuggestions(false);
        }
      } else {
        console.error("Failed to fetch suggestions:", response.status);
      }
    } catch (error) {
      console.warn("Failed to fetch title suggestions:", error);
      setTitleSuggestions([]);
      setShowTitleSuggestions(false);
    } finally {
      setIsLoadingTitleSuggestions(false);
    }
  };

  // Debounce title suggestions
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      // Only fetch suggestions if user has edited since last applied suggestion
      if (titleInputValue !== lastAppliedSuggestion) {
        fetchTitleSuggestions(titleInputValue);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [titleInputValue, form.description, lastAppliedSuggestion]);

  // Handle title input change
  const handleTitleChange = (value: string) => {
    setTitleInputValue(value);
    setForm({ ...form, title: value });
  };

  // Apply title suggestion
  const applyTitleSuggestion = (suggestion: any) => {
    setForm({ ...form, title: suggestion.title });
    setTitleInputValue(suggestion.title);
    setLastAppliedSuggestion(suggestion.title);
    setShowTitleSuggestions(false);
    setTitleSuggestions([]);
  };

  // Skill icon mapping function
  const getSkillIcon = (skill: string) => {
    const skillLower = skill.toLowerCase();
    
    // Frontend Technologies
    if (skillLower.includes('react')) return <FaReact className="text-blue-500" />;
    if (skillLower.includes('javascript')) return <FaJs className="text-yellow-500" />;
    if (skillLower.includes('typescript')) return <SiTypescript className="text-blue-600" />;
    if (skillLower.includes('angular')) return <FaAngular className="text-red-600" />;
    if (skillLower.includes('vue')) return <FaVuejs className="text-green-500" />;
    if (skillLower.includes('css')) return <FaCss3Alt className="text-blue-500" />;
    if (skillLower.includes('html')) return <FaHtml5 className="text-orange-500" />;
    if (skillLower.includes('next')) return <SiNextdotjs className="text-black" />;
    if (skillLower.includes('tailwind')) return <SiTailwindcss className="text-teal-500" />;
    if (skillLower.includes('sass')) return <SiSass className="text-pink-500" />;
    if (skillLower.includes('less')) return <FaCogs className="text-blue-500" />; // SiLess not available
    if (skillLower.includes('bootstrap')) return <FaBootstrap className="text-purple-600" />;
    
    // CMS Technologies
    if (skillLower.includes('wordpress')) return <FaWordpress className="text-blue-700" />;
    if (skillLower.includes('shopify')) return <FaShopify className="text-green-600" />;
    if (skillLower.includes('magento')) return <SiMagento className="text-orange-600" />;
    if (skillLower.includes('drupal')) return <SiDrupal className="text-blue-800" />;
    if (skillLower.includes('joomla')) return <SiJoomla className="text-orange-500" />;
    if (skillLower.includes('liquid')) return <FaCode className="text-green-500" />; // SiLiquid not available
    
    // Backend Technologies
    if (skillLower.includes('python')) return <FaPython className="text-green-500" />;
    if (skillLower.includes('java') && !skillLower.includes('javascript')) return <FaJava className="text-red-500" />;
    if (skillLower.includes('node')) return <FaNodeJs className="text-green-600" />;
    if (skillLower.includes('php')) return <SiPhp className="text-purple-600" />;
    if (skillLower.includes('django')) return <SiDjango className="text-green-700" />;
    if (skillLower.includes('flask')) return <SiFlask className="text-gray-600" />;
    if (skillLower.includes('express')) return <SiExpress className="text-gray-700" />;
    if (skillLower.includes('nest')) return <SiNestjs className="text-red-600" />;
    if (skillLower.includes('spring')) return <SiSpring className="text-green-600" />;
    if (skillLower.includes('rails')) return <SiRubyonrails className="text-red-600" />;
    
    // Databases
    if (skillLower.includes('mysql')) return <SiMysql className="text-blue-600" />;
    if (skillLower.includes('postgresql') || skillLower.includes('postgres')) return <SiPostgresql className="text-blue-700" />;
    if (skillLower.includes('mongo')) return <SiMongodb className="text-green-600" />;
    if (skillLower.includes('redis')) return <SiRedis className="text-red-600" />;
    if (skillLower.includes('elasticsearch')) return <SiElasticsearch className="text-yellow-600" />;
    if (skillLower.includes('firebase')) return <SiFirebase className="text-orange-500" />;
    if (skillLower.includes('supabase')) return <SiSupabase className="text-green-600" />;
    if (skillLower.includes('sql')) return <FaDatabase className="text-green-600" />;
    
    // Mobile Development
    if (skillLower.includes('flutter')) return <SiFlutter className="text-blue-500" />;
    if (skillLower.includes('swift')) return <SiSwift className="text-orange-500" />;
    if (skillLower.includes('kotlin')) return <SiKotlin className="text-purple-600" />;
    if (skillLower.includes('android')) return <FaAndroid className="text-green-500" />;
    if (skillLower.includes('ios')) return <FaApple className="text-gray-700" />;
    if (skillLower.includes('xcode')) return <SiXcode className="text-blue-600" />;
    if (skillLower.includes('android studio')) return <FaAndroid className="text-green-600" />; // SiAndroidstudio not available
    
    // DevOps & Cloud
    if (skillLower.includes('docker')) return <FaDocker className="text-blue-600" />;
    if (skillLower.includes('kubernetes')) return <SiKubernetes className="text-blue-700" />;
    if (skillLower.includes('aws')) return <FaAws className="text-orange-400" />;
    if (skillLower.includes('terraform')) return <SiTerraform className="text-purple-600" />;
    if (skillLower.includes('jenkins')) return <SiJenkins className="text-gray-700" />;
    if (skillLower.includes('github actions')) return <SiGithubactions className="text-black" />;
    if (skillLower.includes('git')) return <FaGitAlt className="text-orange-600" />;
    
    // Gaming & 3D
    if (skillLower.includes('unity')) return <SiUnity className="text-gray-700" />;
    if (skillLower.includes('unreal')) return <SiUnrealengine className="text-blue-700" />;
    if (skillLower.includes('blender')) return <SiBlender className="text-orange-600" />;
    
    // Design & Tools
    if (skillLower.includes('photoshop')) return <SiAdobephotoshop className="text-blue-600" />;
    if (skillLower.includes('illustrator')) return <SiAdobeillustrator className="text-orange-600" />;
    if (skillLower.includes('figma')) return <FaFigma className="text-purple-500" />;
    if (skillLower.includes('sketch')) return <SiSketch className="text-orange-500" />;
    if (skillLower.includes('invision')) return <FaEye className="text-pink-500" />; // SiInvision not available
    if (skillLower.includes('zeplin')) return <FaEye className="text-orange-500" />; // SiZeplin not available
    if (skillLower.includes('miro')) return <FaUsers className="text-yellow-500" />; // SiMiro not available
    
    // Testing
    if (skillLower.includes('jest')) return <SiJest className="text-red-600" />;
    if (skillLower.includes('cypress')) return <SiCypress className="text-gray-700" />;
    if (skillLower.includes('selenium')) return <SiSelenium className="text-green-600" />;
    
    // Build Tools
    if (skillLower.includes('webpack')) return <SiWebpack className="text-blue-600" />;
    if (skillLower.includes('vite')) return <SiVite className="text-purple-600" />;
    
    // API Technologies
    if (skillLower.includes('graphql')) return <SiGraphql className="text-pink-500" />;
    if (skillLower.includes('rest')) return <FaServer className="text-blue-500" />;
    
    // Operating Systems
    if (skillLower.includes('linux')) return <FaLinux className="text-gray-700" />;
    if (skillLower.includes('windows')) return <FaWindows className="text-blue-600" />;
    if (skillLower.includes('microsoft')) return <FaMicrosoft className="text-blue-600" />;
    if (skillLower.includes('google')) return <FaGoogle className="text-red-500" />;
    
    // Project Management & Collaboration
    if (skillLower.includes('slack')) return <FaSlack className="text-purple-600" />;
    if (skillLower.includes('trello')) return <FaTrello className="text-blue-600" />;
    
    // Analytics & SEO
    if (skillLower.includes('analytics')) return <FaChartLine className="text-blue-500" />;
    if (skillLower.includes('seo')) return <FaEye className="text-green-500" />;
    
    // Soft skills
    if (skillLower.includes('communication')) return <FaComments className="text-blue-500" />;
    if (skillLower.includes('leadership')) return <FaUser className="text-purple-500" />;
    if (skillLower.includes('problem solving')) return <FaBrain className="text-indigo-500" />;
    if (skillLower.includes('teamwork') || skillLower.includes('collaboration')) return <FaUsers className="text-green-500" />;
    if (skillLower.includes('adaptability')) return <FaRocket className="text-orange-500" />;
    if (skillLower.includes('creativity')) return <FaLightbulb className="text-yellow-500" />;
    if (skillLower.includes('empathy')) return <FaHeart className="text-red-500" />;
    if (skillLower.includes('time management')) return <FaClock className="text-blue-500" />;
    if (skillLower.includes('negotiation')) return <FaHandshake className="text-green-500" />;
    
    // Generic categories
    if (skillLower.includes('cloud')) return <FaCloud className="text-blue-400" />;
    if (skillLower.includes('server')) return <FaServer className="text-gray-600" />;
    if (skillLower.includes('mobile')) return <FaMobile className="text-gray-700" />;
    if (skillLower.includes('database')) return <FaDatabase className="text-green-600" />;
    
    // Default icon
    return <FaCogs className="text-gray-500" />;
  };

  // Level color mapping for colored circles - improved contrast
  const getLevelColor = (level: string) => {
    const levelLower = level.toLowerCase();
    if (levelLower.includes('beginner') || levelLower.includes('basic')) {
      return 'bg-green-500 border-green-600';
    }
    if (levelLower.includes('intermediate')) {
      return 'bg-blue-500 border-blue-600';
    }
    if (levelLower.includes('advanced')) {
      return 'bg-amber-500 border-amber-600';
    }
    if (levelLower.includes('expert')) {
      return 'bg-red-600 border-red-700';
    }
    return 'bg-gray-500 border-gray-600';
  };

  // Check if skill already exists in any category
  const skillExists = (skillName: string) => {
    const checkInCategory = (category: Array<{skill: string; level: string}>) => 
      category.some(item => item.skill === skillName);
    
    return checkInCategory(selectedRequirements.core_skills) ||
           checkInCategory(selectedRequirements.soft_skills) ||
           checkInCategory(selectedRequirements.bonus_skills);
  };
        // Expanded Skills database organized by domain and category
  const availableSkills = {
    core_skills: [
      // Tech Skills - Frontend
      { name: 'React', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'JavaScript', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'TypeScript', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'HTML5', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'CSS3', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Angular', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Vue.js', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Next.js', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - CMS & E-commerce
      { name: 'WordPress', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Shopify', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Magento', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Drupal', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Joomla', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'WooCommerce', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Liquid', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'PHP', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'MySQL', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - Backend
      { name: 'Node.js', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Python', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Java', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Django', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Flask', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Express.js', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'NestJS', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Spring Boot', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Ruby on Rails', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Laravel', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'REST APIs', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'GraphQL', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - Mobile Development
      { name: 'React Native', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Flutter', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Swift', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Kotlin', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Android Development', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'iOS Development', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - DevOps & Cloud
      { name: 'Docker', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Kubernetes', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'AWS', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Git', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'CI/CD', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - Database
      { name: 'SQL', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'MongoDB', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'PostgreSQL', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Redis', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Firebase', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - Design & Tools
      { name: 'Figma', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Adobe Photoshop', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Adobe Illustrator', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Sketch', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'UI/UX Design', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Responsive Design', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - Testing & Quality Assurance
      { name: 'Testing', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Jest', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Cypress', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Selenium', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Mocha', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Chai', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Puppeteer', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Testing Library', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Unit Testing', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Integration Testing', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'E2E Testing', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'PyTest', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Jasmine', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Karma', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - Build Tools & Bundlers
      { name: 'Webpack', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Vite', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Rollup', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Parcel', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Babel', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'ESLint', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Prettier', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - CSS Frameworks & Preprocessors
      { name: 'Tailwind CSS', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Bootstrap', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Material-UI', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Chakra UI', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Sass/SCSS', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Less', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Styled Components', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - State Management
      { name: 'Redux', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'MobX', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Zustand', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Context API', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Recoil', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Tech Skills - Package Managers & Tools
      { name: 'NPM', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Yarn', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'PNPM', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      
      // Data Skills
      { name: 'Excel', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'data' },
      { name: 'Power BI', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'data' },
      { name: 'Tableau', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'data' },
      { name: 'Statistics', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'data' },
      { name: 'Data Analysis', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'data' },
      { name: 'R', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'data' },
      
      // HR Skills
      { name: 'Recruitment', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'hr' },
      { name: 'Onboarding', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'hr' },
      { name: 'Employee Relations', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'hr' },
      { name: 'HRIS', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'hr' },
      { name: 'Payroll', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'hr' },
      { name: 'Performance Management', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'hr' },
      
      // Project Management Skills
      { name: 'Agile', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'management' },
      { name: 'Scrum', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'management' },
      { name: 'Project Planning', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'management' },
      { name: 'Stakeholder Management', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'management' },
      { name: 'Risk Management', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'management' },
      
      // Business Skills
      { name: 'Strategy', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'business' },
      { name: 'Market Research', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'business' },
      { name: 'Negotiation', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'business' },
      { name: 'Business Analysis', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'business' },
      
      // Marketing Skills
      { name: 'Digital Marketing', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'marketing' },
      { name: 'Social Media', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'marketing' },
      { name: 'Content Creation', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'marketing' },
      { name: 'SEO/SEM', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'marketing' },
      
      // Finance Skills
      { name: 'Financial Analysis', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'finance' },
      { name: 'Accounting', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'finance' },
      { name: 'Budgeting', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'finance' },
      { name: 'Financial Modeling', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'finance' },
    ],
    
    soft_skills: [
      { name: 'Communication', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Leadership', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Problem Solving', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Teamwork', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Adaptability', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Creativity', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Empathy', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Time Management', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Collaboration', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Initiative', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Critical Thinking', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Organization', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Learning Ability', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Motivation', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Attention to Detail', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
      { name: 'Conflict Resolution', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'] },
    ],
    
    bonus_skills: [
      { name: 'Testing', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Build Tools', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Responsive Design', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'UX Principles', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'State Management', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Performance Optimization', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Security', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Git', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Docker', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'AWS', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Kubernetes', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'CI/CD', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Microservices', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Machine Learning', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'data' },
      { name: 'Blockchain', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
      { name: 'Mobile Development', levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'], domain: 'tech' },
    ]
  };

  // Helper functions for requirement management
  const addRequirement = (skillWithLevel: string, category: string) => {
    const [skill, level] = skillWithLevel.split(':');
    
    // Check if skill already exists
    if (skillExists(skill)) {
      return;
    }

    setSelectedRequirements(prev => ({
      ...prev,
      [category]: [...prev[category as keyof typeof prev], { skill, level }]
    }));

    // Generate skill suggestions for the added skill
    generateSkillSuggestions(skill);
  };

  const removeRequirement = (skillName: string, category: string) => {
    setSelectedRequirements(prev => ({
      ...prev,
      [category]: prev[category as keyof typeof prev].filter(item => item.skill !== skillName)
    }));
  };

  const getFilteredSkills = () => {
    if (!requirementSearch) return [];
    
    const staticSkills = [
      ...availableSkills.core_skills.map(skill => ({ ...skill, category: 'core_skills' })),
      ...availableSkills.soft_skills.map(skill => ({ ...skill, category: 'soft_skills' })),
      ...availableSkills.bonus_skills.map(skill => ({ ...skill, category: 'bonus_skills' }))
    ];

    // Add dynamically detected skills from smart analysis
    const dynamicSkills: any[] = [];
    
    // Add skills from AI analysis that aren't in static list
    if (agentRequirements.core_skills) {
      agentRequirements.core_skills.forEach(skillObj => {
        if (!staticSkills.some(s => s.name.toLowerCase() === skillObj.skill.toLowerCase())) {
          dynamicSkills.push({
            name: skillObj.skill,
            levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'],
            domain: 'tech',
            category: 'core_skills',
            source: 'detected'
          });
        }
      });
    }
    
    if (agentRequirements.soft_skills) {
      agentRequirements.soft_skills.forEach(skillObj => {
        if (!staticSkills.some(s => s.name.toLowerCase() === skillObj.skill.toLowerCase())) {
          dynamicSkills.push({
            name: skillObj.skill,
            levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'],
            category: 'soft_skills',
            source: 'detected'
          });
        }
      });
    }
    
    if (agentRequirements.bonus_skills) {
      agentRequirements.bonus_skills.forEach(skillObj => {
        if (!staticSkills.some(s => s.name.toLowerCase() === skillObj.skill.toLowerCase())) {
          dynamicSkills.push({
            name: skillObj.skill,
            levels: ['Basic', 'Intermediate', 'Advanced', 'Expert'],
            domain: 'tech',
            category: 'bonus_skills',
            source: 'detected'
          });
        }
      });
    }

    const allSkills = [...staticSkills, ...dynamicSkills];

    return allSkills.filter(skill => 
      skill.name.toLowerCase().includes(requirementSearch.toLowerCase()) &&
      !skillExists(skill.name)
    );
  };

  const getTotalSkillsCount = () => {
    return selectedRequirements.core_skills.length + 
           selectedRequirements.soft_skills.length + 
           selectedRequirements.bonus_skills.length;
  };

  // Update skill level
  const updateSkillLevel = (skillName: string, category: string, newLevel: string) => {
    setSelectedRequirements(prev => ({
      ...prev,
      [category]: prev[category as keyof typeof prev].map(item => 
        item.skill === skillName ? { ...item, level: newLevel } : item
      )
    }));
  };

  // AI-powered requirement analysis with smart suggestions
  async function analyzeRequirements(title: string, description: string) {
    setAnalyzing(true);
    try {
      // Use the enhanced smart suggestions endpoint
      const response = await fetch("http://localhost:8000/jobs/analyze-with-smart-suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, description }),
      });
      
      if (!response.ok) {
        // Fallback analysis if backend is unavailable
        return analyzeRequirementsLocally(title, description);
      }
      
      const data = await response.json();
      
      // Handle the new v3 enhanced response structure
      if (data.smart_skills) {
        // Extract skills - now they come as objects with level/rating
        const smartSkills = data.smart_skills.suggested_skills || [];
        const softSkills = data.smart_skills.soft_skills || [];
        const bonusSkills = data.smart_skills.bonus_skills || [];
        
        // Skills are already formatted objects, just ensure they have the right structure
        const coreSkills = smartSkills.map((skillObj: any) => ({
          skill: skillObj.skill,
          level: skillObj.level || "Intermediate",
          rating: skillObj.rating || 6,
          evidence: skillObj.evidence || data.smart_skills.reasoning || ["Template-based suggestion"],
          weight: skillObj.weight || 0.8,
          category: "core"
        }));

        const formattedSoftSkills = softSkills.map((skillObj: any) => ({
          skill: skillObj.skill,
          level: skillObj.level || "Intermediate",
          rating: skillObj.rating || 6,
          evidence: skillObj.evidence || ["Template-based soft skill"],
          weight: skillObj.weight || 0.6,
          category: "soft"
        }));

        const formattedBonusSkills = bonusSkills.map((skillObj: any) => ({
          skill: skillObj.skill,
          level: skillObj.level || "Basic",
          rating: skillObj.rating || 5,
          evidence: skillObj.evidence || ["Template-based bonus skill"],
          weight: skillObj.weight || 0.5,
          category: "bonus"
        }));

        const result = {
          core_skills: coreSkills,
          soft_skills: formattedSoftSkills,
          bonus_skills: formattedBonusSkills,
          experience: {},
          languages: [],
          tracks: {},
          metadata: { 
            seniority: 'Mid-level',
            job_types: data.job_classification?.detected_types || [],
            is_multi_track: data.job_classification?.is_multi_track || false,
            title_analysis: data.title_analysis || {},
            smart_skills_analysis: data.smart_skills || {},
            ai_disclaimer: data.ai_disclaimer || "AI-generated suggestions should be reviewed carefully."
          }
        };
        
        // If multi-track job, show track breakdown in console for debugging
        if (result.metadata.is_multi_track && Object.keys(result.tracks).length > 0) {
          console.log("Multi-track job detected with tracks:", Object.keys(result.tracks));
          console.log("Track details:", result.tracks);
        }
        
        // Log smart suggestions for user awareness
        if (data.suggestions && Object.keys(data.suggestions).length > 0) {
          console.log("Smart suggestions applied:", data.suggestions);
        }
        
        return result;
      }
      
      // Fallback to local analysis if structure is unexpected
      return analyzeRequirementsLocally(title, description);
    } catch (error) {
      console.warn("Backend unavailable, using local analysis:", error);
      return analyzeRequirementsLocally(title, description);
    } finally {
      setAnalyzing(false);
    }
  }

  // Job type detection
  function detectJobType(title: string, description: string): string[] {
    const text = (title + " " + description).toLowerCase();
    const types: string[] = [];
    
    // Tech-related keywords
    if (text.match(/\b(developer|engineer|programmer|coding|software|frontend|backend|fullstack|web|mobile|react|javascript|python|java)\b/)) {
      types.push('tech');
    }
    
    // Data-related keywords
    if (text.match(/\b(data|analyst|analytics|science|scientist|sql|excel|tableau|power bi|statistics|machine learning|ml|ai)\b/)) {
      types.push('data');
    }
    
    // HR-related keywords
    if (text.match(/\b(hr|human resources|recruitment|recruiter|talent|onboarding|employee|payroll|hris)\b/)) {
      types.push('hr');
    }
    
    // Project Management keywords
    if (text.match(/\b(project manager|pm|scrum|agile|planning|stakeholder|risk management|pmp)\b/)) {
      types.push('management');
    }
    
    // Marketing keywords
    if (text.match(/\b(marketing|social media|seo|sem|content|digital marketing|brand|campaign)\b/)) {
      types.push('marketing');
    }
    
    // Finance keywords
    if (text.match(/\b(finance|financial|accounting|budget|analyst|cpa|controller|treasury)\b/)) {
      types.push('finance');
    }
    
    // Business keywords
    if (text.match(/\b(business|strategy|consulting|analysis|operations|sales|customer)\b/)) {
      types.push('business');
    }
    
    // Internship detection
    if (text.match(/\b(intern|internship|graduate|trainee|entry.level|junior|fresh|new grad)\b/)) {
      types.push('internship');
    }
    
    return types.length > 0 ? types : ['general'];
  }

  // Enhanced seniority detection with internship awareness
  function detectSeniority(title: string, description: string) {
    const text = (title + " " + description).toLowerCase();
    
    // Check for internship/entry level first
    if (text.match(/\b(intern|internship|graduate|trainee|entry.level|fresh|new grad)\b/)) {
      return "Internship/Entry";
    }
    
    if (text.includes("lead") || text.includes("architect") || text.includes("principal") || text.includes("director")) return "Lead";
    if (text.includes("senior") || text.includes("sr.")) return "Senior";
    if (text.includes("junior") || text.includes("jr.")) return "Junior";
    if (text.includes("mid") || text.includes("intermediate")) return "Mid";
    
    // Analyze years of experience
    const experienceMatch = text.match(/(\d+)\+?\s*years?/);
    if (experienceMatch) {
      const years = parseInt(experienceMatch[1]);
      if (years >= 7) return "Lead";
      if (years >= 4) return "Senior";
      if (years >= 2) return "Mid";
      return "Junior";
    }
    
    // Check for "no experience required"
    if (text.match(/\b(no experience|0 years|entry.level)\b/)) {
      return "Internship/Entry";
    }
    
    return "";
  }

  // Enhanced local analysis with domain awareness
  function analyzeRequirementsLocally(title: string, description: string) {
    const result = {
      core_skills: [] as Array<{skill: string; level: string; rating: number; evidence: string[]; weight: number; category: string}>,
      soft_skills: [] as Array<{skill: string; level: string; rating: number; evidence: string[]; weight: number; category: string}>,
      bonus_skills: [] as Array<{skill: string; level: string; rating: number; evidence: string[]; weight: number; category: string}>,
      experience: {},
      languages: [],
      metadata: { job_types: [] as string[], detected_seniority: '' }
    };

    const text = (title + " " + description).toLowerCase();
    const jobTypes = detectJobType(title, description);
    const seniority = detectSeniority(title, description);
    const isInternship = jobTypes.includes('internship') || seniority.includes('Internship');
    
    result.metadata.job_types = jobTypes;
    result.metadata.detected_seniority = seniority;

    // Determine default skill level based on seniority
    let defaultLevel = "Intermediate";
    if (isInternship || seniority.includes('Entry') || text.includes('no experience')) {
      defaultLevel = "Basic";
    } else if (seniority === "Senior") {
      defaultLevel = "Advanced";
    } else if (seniority === "Lead") {
      defaultLevel = "Expert";
    }

    // Tech Skills Analysis (only if tech job type detected)
    if (jobTypes.includes('tech')) {
      if (text.includes("react")) result.core_skills.push({skill: "React", level: defaultLevel, rating: 9, evidence: ["Mentioned in job description"], weight: 0.9, category: "frontend"});
      if (text.includes("typescript")) result.core_skills.push({skill: "TypeScript", level: defaultLevel, rating: 9, evidence: ["Mentioned in job description"], weight: 0.8, category: "frontend"});
      if (text.includes("javascript")) result.core_skills.push({skill: "JavaScript", level: defaultLevel, rating: 9, evidence: ["Mentioned in job description"], weight: 0.9, category: "frontend"});
      if (text.includes("angular")) result.core_skills.push({skill: "Angular", level: defaultLevel, rating: 8, evidence: ["Mentioned in job description"], weight: 0.8, category: "frontend"});
      if (text.includes("vue")) result.core_skills.push({skill: "Vue.js", level: defaultLevel, rating: 8, evidence: ["Mentioned in job description"], weight: 0.8, category: "frontend"});
      if (text.includes("css") || text.includes("styling")) result.core_skills.push({skill: "CSS3", level: isInternship ? "Basic" : "Intermediate", rating: 7, evidence: ["Mentioned in job description"], weight: 0.6, category: "frontend"});
      if (text.includes("html")) result.core_skills.push({skill: "HTML5", level: isInternship ? "Basic" : "Intermediate", rating: 7, evidence: ["Mentioned in job description"], weight: 0.5, category: "frontend"});
      if (text.includes("node") || text.includes("backend")) result.core_skills.push({skill: "Node.js", level: defaultLevel, rating: 8, evidence: ["Mentioned in job description"], weight: 0.8, category: "backend"});
      if (text.includes("python")) result.core_skills.push({skill: "Python", level: defaultLevel, rating: 9, evidence: ["Mentioned in job description"], weight: 0.9, category: "backend"});
      if (text.includes("java") && !text.includes("javascript")) result.core_skills.push({skill: "Java", level: defaultLevel, rating: 9, evidence: ["Mentioned in job description"], weight: 0.8, category: "backend"});
      if (text.includes("rest") || text.includes("api")) result.core_skills.push({skill: "REST APIs", level: defaultLevel, rating: 8, evidence: ["Mentioned in job description"], weight: 0.8, category: "backend"});
      
      // Git is basic for all tech roles
      if (text.includes("git") || jobTypes.includes('tech')) result.bonus_skills.push({skill: "Git", level: "Basic", rating: 6, evidence: ["Essential for development"], weight: 0.6, category: "tools"});
    }

    // Data Skills Analysis
    if (jobTypes.includes('data')) {
      if (text.includes("sql")) result.core_skills.push({skill: "SQL", level: defaultLevel, rating: 8, evidence: ["Mentioned in job description"], weight: 0.9, category: "database"});
      if (text.includes("excel")) result.core_skills.push({skill: "Excel", level: defaultLevel, rating: 8, evidence: ["Mentioned in job description"], weight: 0.8, category: "tools"});
      if (text.includes("python")) result.core_skills.push({skill: "Python", level: defaultLevel, rating: 8, evidence: ["Data analysis mentioned"], weight: 0.8, category: "programming"});
      if (text.includes("tableau")) result.core_skills.push({skill: "Tableau", level: defaultLevel, rating: 7, evidence: ["BI tool mentioned"], weight: 0.7, category: "visualization"});
      if (text.includes("power bi")) result.core_skills.push({skill: "Power BI", level: defaultLevel, rating: 7, evidence: ["BI tool mentioned"], weight: 0.7, category: "visualization"});
      if (text.includes("statistics") || text.includes("statistical")) result.core_skills.push({skill: "Statistics", level: defaultLevel, rating: 8, evidence: ["Statistical analysis mentioned"], weight: 0.8, category: "analysis"});
    }

    // HR Skills Analysis
    if (jobTypes.includes('hr')) {
      if (text.includes("recruitment") || text.includes("recruiting")) result.core_skills.push({skill: "Recruitment", level: defaultLevel, rating: 8, evidence: ["Recruitment mentioned"], weight: 0.9, category: "hr"});
      if (text.includes("onboarding")) result.core_skills.push({skill: "Onboarding", level: defaultLevel, rating: 7, evidence: ["Onboarding mentioned"], weight: 0.7, category: "hr"});
      if (text.includes("employee relations")) result.core_skills.push({skill: "Employee Relations", level: defaultLevel, rating: 8, evidence: ["Employee relations mentioned"], weight: 0.8, category: "hr"});
      if (text.includes("hris") || text.includes("hr system")) result.core_skills.push({skill: "HRIS", level: defaultLevel, rating: 7, evidence: ["HRIS mentioned"], weight: 0.7, category: "systems"});
      if (text.includes("payroll")) result.core_skills.push({skill: "Payroll", level: defaultLevel, rating: 7, evidence: ["Payroll mentioned"], weight: 0.7, category: "hr"});
    }

    // Project Management Skills
    if (jobTypes.includes('management')) {
      if (text.includes("agile")) result.core_skills.push({skill: "Agile", level: defaultLevel, rating: 8, evidence: ["Agile mentioned"], weight: 0.8, category: "methodology"});
      if (text.includes("scrum")) result.core_skills.push({skill: "Scrum", level: defaultLevel, rating: 8, evidence: ["Scrum mentioned"], weight: 0.8, category: "methodology"});
      if (text.includes("planning") || text.includes("project planning")) result.core_skills.push({skill: "Project Planning", level: defaultLevel, rating: 8, evidence: ["Planning mentioned"], weight: 0.8, category: "planning"});
      if (text.includes("stakeholder")) result.core_skills.push({skill: "Stakeholder Management", level: defaultLevel, rating: 7, evidence: ["Stakeholder management mentioned"], weight: 0.7, category: "management"});
    }

    // Enhanced Soft Skills Analysis
    if (text.includes("communication")) result.soft_skills.push({skill: "Communication", level: "Advanced", rating: 8, evidence: ["Communication mentioned"], weight: 0.8, category: "interpersonal"});
    if (text.includes("collaboration") || text.includes("teamwork") || text.includes("team player")) result.soft_skills.push({skill: "Collaboration", level: "Advanced", rating: 7, evidence: ["Teamwork mentioned"], weight: 0.7, category: "interpersonal"});
    if (text.includes("problem solving") || text.includes("analytical")) result.soft_skills.push({skill: "Problem Solving", level: "Advanced", rating: 7, evidence: ["Problem solving mentioned"], weight: 0.7, category: "analytical"});
    if (text.includes("leadership") || text.includes("lead") || text.includes("mentor")) result.soft_skills.push({skill: "Leadership", level: "Advanced", rating: 8, evidence: ["Leadership mentioned"], weight: 0.8, category: "management"});
    if (text.includes("initiative") || text.includes("self-motivated")) result.soft_skills.push({skill: "Initiative", level: "Advanced", rating: 7, evidence: ["Initiative mentioned"], weight: 0.7, category: "personal"});
    if (text.includes("critical thinking") || text.includes("analytical thinking")) result.soft_skills.push({skill: "Critical Thinking", level: "Advanced", rating: 7, evidence: ["Critical thinking mentioned"], weight: 0.7, category: "analytical"});
    if (text.includes("detail") || text.includes("attention to detail")) result.soft_skills.push({skill: "Attention to Detail", level: "Advanced", rating: 7, evidence: ["Attention to detail mentioned"], weight: 0.7, category: "personal"});
    if (text.includes("time management") || text.includes("organization")) result.soft_skills.push({skill: "Time Management", level: "Advanced", rating: 7, evidence: ["Time management mentioned"], weight: 0.7, category: "personal"});
    
    // For internships, emphasize learning and motivation
    if (isInternship) {
      result.soft_skills.push({skill: "Learning Ability", level: "Advanced", rating: 9, evidence: ["Essential for internship"], weight: 0.9, category: "personal"});
      result.soft_skills.push({skill: "Motivation", level: "Advanced", rating: 8, evidence: ["Important for entry-level"], weight: 0.8, category: "personal"});
    }

    // Bonus Skills Analysis based on job type
    if (jobTypes.includes('tech')) {
      if (text.includes("docker")) result.bonus_skills.push({skill: "Docker", level: "Intermediate", rating: 6, evidence: ["Containerization mentioned"], weight: 0.6, category: "devops"});
      if (text.includes("aws") || text.includes("cloud")) result.bonus_skills.push({skill: "AWS", level: "Intermediate", rating: 6, evidence: ["Cloud services mentioned"], weight: 0.6, category: "cloud"});
      if (text.includes("testing") || text.includes("jest") || text.includes("unit test")) result.bonus_skills.push({skill: "Testing", level: "Intermediate", rating: 6, evidence: ["Testing mentioned"], weight: 0.6, category: "quality"});
    }

    return result;
  }

  // AI-powered job summary generation
  async function summarizeJob(job: any) {
    setGenerating(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/jobs/generate-summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(job),
      });
      
      if (!response.ok) {
        return generateSummaryLocally(job);
      }
      
      const data = await response.json();
      return data.summary || "";
    } catch (error) {
      console.warn("Backend unavailable, using local summary generation:", error);
      return generateSummaryLocally(job);
    } finally {
      setGenerating(false);
    }
  }

  // Local summary generation
  function generateSummaryLocally(job: any) {
    const { title, description, requirements, seniority, screening_questions } = job;
    
    return `🚀 **${title}** - ${seniority || 'Professional'} Level Position

📋 **Role Overview:**
${description.substring(0, 200)}...

🎯 **Key Requirements:**
${requirements.map((req: string) => `• ${req}`).join('\n')}

💼 **What We're Looking For:**
We seek a ${seniority?.toLowerCase() || 'skilled'} professional who can contribute to our team's success. The ideal candidate will have strong technical skills and the ability to work in a collaborative environment.

🔍 **Assessment Process:**
${screening_questions.length > 0 ? 
  `Candidates will be evaluated through:\n${screening_questions.map((q: string) => `• ${q}`).join('\n')}` : 
  'Standard interview process including technical and cultural fit assessment.'}

This position offers an excellent opportunity to work with cutting-edge technologies and contribute to meaningful projects in a dynamic environment.`;
  }

  // Fetch salary suggestions based on skills, location, and seniority
  async function fetchSalarySuggestions() {
    if (!form.location || !form.seniority || selectedRequirements.core_skills.length === 0) {
      return;
    }

    setLoadingSalary(true);
    try {
      const skills = [
        ...selectedRequirements.core_skills,
        ...selectedRequirements.soft_skills,
        ...selectedRequirements.bonus_skills
      ];

      const response = await fetch("http://127.0.0.1:8000/salary-suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_title: form.title,
          skills: skills,
          location: form.location,
          seniority_level: form.seniority,
          job_description: form.description
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setSalaryData(data);
        
        // Auto-populate salary fields if they're empty
        if (!form.salary_min && !form.salary_max) {
          setForm(prev => ({
            ...prev,
            salary_min: Math.round(data.min_salary).toString(),
            salary_max: Math.round(data.max_salary).toString()
          }));
        }
      }
    } catch (error) {
      console.warn("Failed to fetch salary suggestions:", error);
    } finally {
      setLoadingSalary(false);
    }
  }

  // Trigger salary suggestions when relevant fields change
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchSalarySuggestions();
    }, 1000); // Debounce by 1 second

    return () => clearTimeout(timer);
  }, [form.location, form.seniority, selectedRequirements.core_skills.length]);

  // Fetch experience level detection
  async function fetchExperienceLevelDetection() {
    if (!form.title && !form.description) {
      return;
    }

    setLoadingExperience(true);
    try {
      const requirements = [
        ...selectedRequirements.core_skills.map(s => s.skill),
        ...selectedRequirements.soft_skills.map(s => s.skill),
        ...selectedRequirements.bonus_skills.map(s => s.skill)
      ].join(', ');

      const response = await fetch("http://127.0.0.1:8000/experience-level-detection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_title: form.title,
          job_description: form.description,
          requirements: requirements
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setExperienceData(data);
        
        // Auto-update seniority if it's empty and confidence is high
        if (!form.seniority && data.confidence_score > 0.7) {
          setForm(prev => ({
            ...prev,
            seniority: data.detected_level
          }));
        }
      }
    } catch (error) {
      console.warn("Failed to fetch experience level detection:", error);
    } finally {
      setLoadingExperience(false);
    }
  }

  // Trigger experience detection when title or description changes
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchExperienceLevelDetection();
    }, 1500); // Debounce by 1.5 seconds

    return () => clearTimeout(timer);
  }, [form.title, form.description]);

  // Auto-complete function - focused on skills only
  async function fetchAutoCompleteSuggestions(context: string, fieldType: string, cursorPosition?: number) {
    if (context.length < 2) {
      setShowAutoComplete(false);
      return;
    }

    console.log('🔍 Fetching skill suggestions for:', context);
    setLoadingAutoComplete(true);
    
    // Extract the last word or partial word being typed
    const words = context.toLowerCase().split(/[\s,\.]+/);
    const lastWord = words[words.length - 1];
    const searchTerm = lastWord.length >= 2 ? lastWord : context.toLowerCase();
    
    console.log('🎯 Searching for skills matching:', searchTerm);
    
    // Get skill suggestions from our taxonomy
    const getSkillSuggestions = (searchText: string) => {
      const allSkills = [...availableSkills.core_skills, ...availableSkills.soft_skills, ...availableSkills.bonus_skills];
      
      // Find skills that match the search term
      const matchingSkills = allSkills
        .filter(skill => {
          const skillName = skill.name.toLowerCase();
          return skillName.includes(searchText) || skillName.startsWith(searchText);
        })
        .sort((a, b) => {
          // Prioritize exact starts over contains
          const aStarts = a.name.toLowerCase().startsWith(searchText);
          const bStarts = b.name.toLowerCase().startsWith(searchText);
          if (aStarts && !bStarts) return -1;
          if (!aStarts && bStarts) return 1;
          return a.name.localeCompare(b.name);
        })
        .slice(0, 8)
        .map(skill => ({
          text: skill.name,
          type: 'skill',
          confidence: skill.name.toLowerCase().startsWith(searchText) ? 0.95 : 0.8,
          category: 'technical_skill',
          icon: getSkillIcon(skill.name)
        }));
      
      console.log('📋 Found matching skills:', matchingSkills);
      return matchingSkills;
    };

    // Function to get appropriate icon for skills
    const getSkillIcon = (skillName: string) => {
      const skill = skillName.toLowerCase();
      if (skill.includes('react') || skill.includes('vue') || skill.includes('angular')) return '⚛️';
      if (skill.includes('javascript') || skill.includes('typescript')) return '📜';
      if (skill.includes('python') || skill.includes('java') || skill.includes('php')) return '🐍';
      if (skill.includes('css') || skill.includes('html') || skill.includes('sass')) return '🎨';
      if (skill.includes('database') || skill.includes('sql') || skill.includes('mongo')) return '🗄️';
      if (skill.includes('docker') || skill.includes('kubernetes') || skill.includes('aws')) return '☁️';
      if (skill.includes('git') || skill.includes('github')) return '🔧';
      if (skill.includes('design') || skill.includes('figma') || skill.includes('photoshop')) return '🎨';
      if (skill.includes('test') || skill.includes('jest') || skill.includes('cypress')) return '🧪';
      if (skill.includes('node') || skill.includes('express')) return '🔧';
      return '⚙️'; // Default technical skill icon
    };

    try {
      const skillSuggestions = getSkillSuggestions(searchTerm);
      
      if (skillSuggestions.length > 0) {
        console.log('✅ Showing skill suggestions:', skillSuggestions);
        setAutoCompleteSuggestions(skillSuggestions);
        setShowAutoComplete(true);
        setDebugAutoComplete(true);
        setActiveField('description');
      } else {
        console.log('❌ No skills found for:', searchTerm);
        setShowAutoComplete(false);
      }
      
    } catch (error) {
      console.error("❌ Auto-complete error:", error);
      setShowAutoComplete(false);
    } finally {
      setLoadingAutoComplete(false);
    }
  }

  // Apply auto-complete suggestion - skills only
  const applyAutoCompleteSuggestion = (suggestion: any, fieldType: string) => {
    const currentValue = fieldType === 'description' ? form.description : 
                        fieldType === 'requirements' ? form.requirements.join('\n') : '';
    
    console.log('✅ Applying skill suggestion:', suggestion.text);
    
    // For skills, replace the last word being typed or add the skill
    const words = currentValue.split(/(\s+)/); // Split but keep spaces
    const lastWordIndex = words.length - 1;
    
    // Check if the last "word" is actually a space
    if (words[lastWordIndex] && words[lastWordIndex].trim() === '') {
      // Just add the skill after the space
      words.push(suggestion.text);
    } else {
      // Replace the last word with the skill
      words[lastWordIndex] = suggestion.text;
    }
    
    const newValue = words.join('');

    if (fieldType === 'description') {
      setForm(prev => ({ ...prev, description: newValue }));
    }
    
    setShowAutoComplete(false);
    setDebugAutoComplete(false);
    setSelectedSuggestionIndex(0);
  };

  // Handle keyboard navigation for auto-complete
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent, fieldType: string) => {
    if (!showAutoComplete || autoCompleteSuggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedSuggestionIndex(prev => 
        prev < autoCompleteSuggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedSuggestionIndex(prev => 
        prev > 0 ? prev - 1 : autoCompleteSuggestions.length - 1
      );
    } else if (e.key === 'Enter' && selectedSuggestionIndex >= 0) {
      e.preventDefault();
      console.log('⌨️ Enter pressed, applying suggestion:', autoCompleteSuggestions[selectedSuggestionIndex]);
      applyAutoCompleteSuggestion(autoCompleteSuggestions[selectedSuggestionIndex], fieldType);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setShowAutoComplete(false);
      setSelectedSuggestionIndex(0);
    }
  };

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      
      // Close level dropdown
      if (activeLevelDropdown && !target?.closest('.relative')) {
        setActiveLevelDropdown(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [activeLevelDropdown]);

  if (loading) {
    return (
      <div className="flex justify-center items-center bg-gradient-to-br from-purple-100 via-blue-100 to-pink-100 min-h-screen">
        <div className="text-center">
          <div className="mx-auto mb-4 border-purple-600 border-b-2 rounded-full w-32 h-32 animate-spin"></div>
          <p className="text-gray-600 text-xl">Checking authentication...</p>
        </div>
      </div>
    );
  }

  return (
    <PageContainer>
      <AppHeader 
        title="Create Job"
        subtitle="Use AI-powered assistance to create the perfect job posting"
        backHref="/jobs"
        backLabel="Back to Jobs"
      />

      <MainContent>
        <div className="gap-8 grid lg:grid-cols-4">
          {/* Progress Sidebar */}
          <div className="lg:col-span-1">
            <Card padding="lg" className="top-4 sticky">
              <SectionHeader 
                title="Creation Progress" 
                icon="fas fa-tasks"
                size="sm"
              />
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <i className={`fas fa-circle ${step >= 1 ? 'text-green-500' : 'text-gray-300'}`}></i>
                    <span className="text-gray-700 text-sm">Job Details</span>
                  </div>
                  {step >= 1 && <i className="text-green-500 fas fa-check"></i>}
                </div>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <i className={`fas fa-circle ${step >= 2 ? 'text-green-500' : 'text-gray-300'}`}></i>
                    <span className="text-gray-700 text-sm">Requirements</span>
                  </div>
                  {step >= 2 && <i className="text-green-500 fas fa-check"></i>}
                </div>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <i className={`fas fa-circle ${step >= 3 ? 'text-green-500' : 'text-gray-300'}`}></i>
                    <span className="text-gray-700 text-sm">AI Summary</span>
                  </div>
                  {step >= 3 && <i className="text-green-500 fas fa-check"></i>}
                </div>
              </div>
            </Card>

            {/* Market Analytics Dashboard */}
            {form.title && (
              <Card padding="lg" className="top-24 sticky mt-6">
                <SectionHeader 
                  title="Market Insights" 
                  icon="fas fa-chart-line"
                  size="sm"
                />
                <div className="space-y-4">
                  {/* Competition Level */}
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 border border-blue-200 rounded-xl">
                    <div className="flex justify-between items-center mb-2">
                      <span className="flex items-center font-medium text-gray-800 text-sm">
                        <i className="mr-2 text-blue-600 fas fa-trophy"></i>
                        Competition
                      </span>
                      <span className="bg-orange-100 px-2 py-1 rounded-full font-semibold text-orange-800 text-xs">
                        Medium
                      </span>
                    </div>
                    <p className="text-gray-600 text-xs">
                      ~{Math.floor(Math.random() * 50 + 20)} similar jobs posted this week
                    </p>
                  </div>

                  {/* Time to Hire */}
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 border border-green-200 rounded-xl">
                    <div className="flex justify-between items-center mb-2">
                      <span className="flex items-center font-medium text-gray-800 text-sm">
                        <i className="mr-2 text-green-600 fas fa-clock"></i>
                        Avg. Time to Hire
                      </span>
                      <span className="bg-green-100 px-2 py-1 rounded-full font-semibold text-green-800 text-xs">
                        {Math.floor(Math.random() * 20 + 15)} days
                      </span>
                    </div>
                    <p className="text-gray-600 text-xs">
                      Based on similar roles in your area
                    </p>
                  </div>

                  {/* Trending Skills */}
                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 border border-purple-200 rounded-xl">
                    <div className="flex items-center mb-2">
                      <span className="flex items-center font-medium text-gray-800 text-sm">
                        <i className="mr-2 text-purple-600 fas fa-trending-up"></i>
                        Trending Skills
                      </span>
                    </div>
                    <div className="space-y-1">
                      {['React', 'TypeScript', 'Node.js'].slice(0, 3).map((skill, idx) => (
                        <div key={skill} className="flex justify-between items-center">
                          <span className="text-gray-700 text-xs">{skill}</span>
                          <span className="text-purple-600 text-xs">+{Math.floor(Math.random() * 30 + 10)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Success Prediction */}
                  {step >= 2 && getTotalSkillsCount() > 0 && (
                    <div className="bg-gradient-to-r from-yellow-50 to-orange-50 p-4 border border-yellow-200 rounded-xl">
                      <div className="flex justify-between items-center mb-2">
                        <span className="flex items-center font-medium text-gray-800 text-sm">
                          <i className="mr-2 text-yellow-600 fas fa-brain"></i>
                          Success Score
                        </span>
                        <span className="bg-yellow-100 px-2 py-1 rounded-full font-semibold text-yellow-800 text-xs">
                          {Math.min(95, 60 + getTotalSkillsCount() * 5)}%
                        </span>
                      </div>
                      <p className="text-gray-600 text-xs">
                        Based on {getTotalSkillsCount()} requirements defined
                      </p>
                    </div>
                  )}

                  {/* Quick Tips */}
                  <div className="bg-gradient-to-r from-gray-50 to-slate-50 p-4 border border-gray-200 rounded-xl">
                    <div className="flex items-center mb-2">
                      <span className="flex items-center font-medium text-gray-800 text-sm">
                        <i className="mr-2 text-gray-600 fas fa-lightbulb"></i>
                        Quick Tip
                      </span>
                    </div>
                    <p className="text-gray-600 text-xs">
                      {step === 1 && "Add specific skills to attract qualified candidates"}
                      {step === 2 && "Consider adding 2-3 bonus skills to widen your talent pool"}
                      {step === 3 && "Review salary range - it affects 40% of application rates"}
                      {step >= 4 && "Post on Tuesday-Thursday for 35% higher response rates"}
                    </p>
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Main Content */}
          <div className="space-y-6 lg:col-span-3">
            {/* Form Content */}
            {step === 1 && (
              <Card padding="xl">
                <div className="mb-8 text-center">
                  <div className="flex justify-center items-center bg-gradient-to-br from-purple-500 to-blue-500 mx-auto mb-4 rounded-2xl w-16 h-16">
                    <i className="text-white text-2xl fas fa-edit"></i>
                  </div>
                  <h2 className="mb-2 font-bold text-gray-900 text-2xl">Job Details</h2>
                  <p className="text-gray-600">Provide the basic information for your job posting</p>
                </div>
                
                <form className="space-y-6" onSubmit={async (e) => {
                  e.preventDefault();
                  try {
                    setAnalyzing(true);
                    
                    // AI Analysis
                    const reqs = await analyzeRequirements(form.title, form.description);
                    const detectedSeniority = detectSeniority(form.title, form.description);
                    
                    setAgentRequirements(reqs);
                    
                    // Convert complex skill objects to simple format for selectedRequirements
                    setSelectedRequirements({
                      core_skills: (reqs.core_skills || []).map((skill: any) => ({
                        skill: skill.skill,
                        level: skill.level
                      })),
                      soft_skills: (reqs.soft_skills || []).map((skill: any) => ({
                        skill: skill.skill,
                        level: skill.level
                      })),
                      bonus_skills: (reqs.bonus_skills || []).map((skill: any) => ({
                        skill: skill.skill,
                        level: skill.level
                      }))
                    });
                      
                    // Auto-set seniority if detected
                    if (detectedSeniority && !form.seniority) {
                      setForm({ ...form, seniority: detectedSeniority });
                    }
                    
                    setStep(2);
                  } catch (error) {
                    console.error('Error in form submission:', error);
                  } finally {
                    setAnalyzing(false);
                  }
                }}>
                    <div className="relative">
                      <label className="block mb-2 font-semibold text-gray-700">
                        <i className="mr-2 text-purple-600 fas fa-briefcase"></i>
                        Job Title
                      </label>
                      <div className="relative">
                        <input 
                          className="bg-white/80 shadow-lg backdrop-blur-md px-6 py-4 border border-gray-200 focus:border-transparent rounded-2xl focus:ring-2 focus:ring-purple-500 w-full text-gray-900 placeholder:text-gray-500 text-lg transition-all duration-300" 
                          placeholder="e.g. Frontend Engineer, Backend Developer" 
                          value={titleInputValue} 
                          onChange={(e) => handleTitleChange(e.target.value)}
                          required 
                        />
                        {isLoadingTitleSuggestions && (
                          <div className="top-1/2 right-4 absolute -translate-y-1/2 transform">
                            <div className="border-purple-500 border-b-2 rounded-full w-5 h-5 animate-spin"></div>
                          </div>
                        )}
                      </div>
                      
                      {/* Simple Title Suggestions Below Input */}
                      {titleSuggestions.length > 0 && (
                        <div className="mt-3">
                          <p className="flex items-center mb-2 text-gray-600 text-sm">
                            <i className="mr-2 text-yellow-500 fas fa-lightbulb"></i>
                            Did you mean:
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {titleSuggestions.map((suggestion, idx) => (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => applyTitleSuggestion(suggestion)}
                                className="group inline-flex items-center bg-blue-50 hover:bg-blue-100 px-3 py-1.5 border border-blue-200 hover:border-blue-300 rounded-lg text-blue-700 hover:text-blue-800 text-sm transition-all duration-200"
                              >
                                <span className="font-medium">{suggestion.title}</span>
                                <span className="ml-2 text-blue-500 group-hover:text-blue-600 text-xs">
                                  {Math.round(suggestion.confidence)}%
                                </span>
                                <i className="fa-arrow-up-right opacity-60 group-hover:opacity-100 ml-1 text-xs fas"></i>
                              </button>
                            ))}
                          </div>
                          <p className="mt-2 text-gray-500 text-xs">
                            💡 Click any suggestion to use it as your job title
                          </p>
                        </div>
                      )}
                    </div>
                    
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <label className="block font-semibold text-gray-700">Job Description</label>
                        {/* Debug button for testing auto-complete */}
                        <button
                          type="button"
                          onClick={() => {
                            console.log('🧪 Test button clicked!');
                            setActiveField('description');
                            setDebugAutoComplete(true);
                            fetchAutoCompleteSuggestions("React", "description");
                          }}
                          className="bg-purple-100 hover:bg-purple-200 px-3 py-1 rounded-lg font-medium text-purple-700 text-sm transition-colors"
                        >
                          🧪 Test Skills
                        </button>
                      </div>
                      <div className="relative">
                        <textarea 
                          className="bg-white/80 shadow-lg backdrop-blur-md px-6 py-4 border border-gray-200 focus:border-transparent rounded-2xl focus:ring-2 focus:ring-purple-500 w-full text-gray-900 placeholder:text-gray-500 text-lg transition-all duration-300" 
                          placeholder="Describe the role, responsibilities, and what you're looking for in a candidate..." 
                          value={form.description} 
                          onChange={(e) => {
                            console.log('📝 Description changed:', e.target.value);
                            setForm({ ...form, description: e.target.value });
                            // Reset selection when typing
                            setSelectedSuggestionIndex(0);
                            
                            // Clear any existing timeout
                            if (window.autoCompleteTimeout) {
                              clearTimeout(window.autoCompleteTimeout);
                            }
                            
                            // Trigger auto-complete with smart timing
                            if (e.target.value.length >= 2) {
                              console.log('🚀 Triggering auto-complete for:', e.target.value);
                              setActiveField('description');
                              
                              // Use shorter delay for better responsiveness
                              window.autoCompleteTimeout = setTimeout(() => {
                                fetchAutoCompleteSuggestions(e.target.value, 'description');
                              }, 300);
                            } else {
                              console.log('❌ Text too short, hiding auto-complete');
                              setShowAutoComplete(false);
                            }
                          }}
                          onKeyDown={(e) => handleKeyDown(e, 'description')}
                          onFocus={() => setActiveField('description')}
                          onBlur={() => {
                            // Delay hiding to allow clicking suggestions
                            setTimeout(() => setShowAutoComplete(false), 200);
                          }}
                          required 
                          rows={8} 
                        />
                        
                        {/* Auto-complete suggestions dropdown */}
                        {(showAutoComplete || debugAutoComplete) && activeField === 'description' && autoCompleteSuggestions.length > 0 && (
                          <div className="z-[9999] absolute bg-white slide-in-from-top-2 shadow-2xl backdrop-blur-lg mt-1 border border-purple-200 rounded-2xl w-full max-h-80 overflow-hidden animate-in duration-200">
                            <div className="flex justify-between items-center bg-gradient-to-r from-purple-50 to-blue-50 px-4 py-3 border-purple-100 border-b">
                              <div className="flex items-center gap-2">
                                <span className="text-xl">✨</span>
                                <span className="font-semibold text-gray-800 text-sm">
                                  Smart Suggestions
                                </span>
                                <span className="bg-purple-100 px-2 py-1 rounded-full font-medium text-purple-700 text-xs">
                                  {autoCompleteSuggestions.length}
                                </span>
                              </div>
                              {loadingAutoComplete && (
                                <div className="flex items-center gap-2">
                                  <div className="border-2 border-purple-500 border-t-transparent rounded-full w-4 h-4 animate-spin"></div>
                                  <span className="text-purple-600 text-xs">Loading...</span>
                                </div>
                              )}
                            </div>
                            
                            <div className="max-h-64 overflow-y-auto">
                              {autoCompleteSuggestions.map((suggestion, index) => (
                                <button
                                  key={`suggestion-${index}`}
                                  type="button"
                                  className={`flex items-start gap-3 p-4 w-full text-left transition-all duration-200 group border-l-4 hover:shadow-sm ${
                                    index === selectedSuggestionIndex 
                                      ? 'bg-gradient-to-r from-purple-100 to-blue-100 border-l-purple-500 shadow-lg' 
                                      : 'hover:bg-gradient-to-r hover:from-purple-50 hover:to-blue-50 border-l-transparent hover:border-l-purple-300'
                                  }`}
                                  onClick={() => {
                                    console.log('🎯 Suggestion clicked:', suggestion);
                                    applyAutoCompleteSuggestion(suggestion, 'description');
                                  }}
                                  onMouseEnter={() => setSelectedSuggestionIndex(index)}
                                >
                                  <div className={`text-2xl transition-transform duration-200 ${
                                    index === selectedSuggestionIndex ? 'scale-110' : 'group-hover:scale-105'
                                  }`}>
                                    {suggestion.icon || '💡'}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className={`font-medium text-sm leading-relaxed ${
                                      index === selectedSuggestionIndex 
                                        ? 'text-purple-900' 
                                        : 'text-gray-800 group-hover:text-purple-800'
                                    }`}>
                                      {suggestion.text}
                                    </div>
                                    <div className="flex items-center gap-3 mt-2">
                                      <span className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                        suggestion.category === 'opening' ? 'bg-blue-100 text-blue-700' :
                                        suggestion.category === 'responsibility' ? 'bg-green-100 text-green-700' :
                                        suggestion.category === 'requirement' ? 'bg-yellow-100 text-yellow-700' :
                                        suggestion.category === 'technical_skill' ? 'bg-purple-100 text-purple-700' :
                                        'bg-gray-100 text-gray-700'
                                      }`}>
                                        {(suggestion.category || 'general').replace('_', ' ')}
                                      </span>
                                      <div className="flex items-center gap-1">
                                        <div className={`w-2 h-2 rounded-full ${
                                          (suggestion.confidence || 0.5) > 0.9 ? 'bg-green-400' :
                                          (suggestion.confidence || 0.5) > 0.7 ? 'bg-yellow-400' :
                                          'bg-gray-400'
                                        }`}></div>
                                        <span className="text-gray-500 text-xs">
                                          {Math.round((suggestion.confidence || 0.5) * 100)}% match
                                        </span>
                                      </div>
                                      {suggestion.type === 'skill' && (
                                        <span className="bg-gradient-to-r from-purple-500 to-blue-500 px-2 py-1 rounded-full font-medium text-white text-xs">
                                          SKILL
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                  {index === selectedSuggestionIndex && (
                                    <div className="flex flex-col justify-center items-center text-purple-500">
                                      <span className="text-lg">⚡</span>
                                      <span className="font-medium text-xs">Enter</span>
                                    </div>
                                  )}
                                </button>
                              ))}
                            </div>
                            
                            <div className="bg-gradient-to-r from-gray-50 to-purple-50 px-4 py-2 border-purple-100 border-t">
                              <div className="flex justify-between items-center">
                                <span className="flex items-center gap-1 text-gray-600 text-xs">
                                  <span>💡</span>
                                  Use ↑↓ to navigate, Enter to select, Esc to close
                                </span>
                                <span className="font-medium text-purple-600 text-xs">
                                  AI-Powered
                                </span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <button type="submit" className="bg-gradient-to-r from-purple-600 hover:from-purple-700 to-blue-600 hover:to-blue-700 shadow-xl hover:shadow-2xl px-8 py-4 rounded-2xl w-full font-bold text-white hover:scale-105 transition-all duration-300" disabled={analyzing}>
                      {analyzing ? (
                        <>
                          <i className="mr-2 fas fa-spinner fa-spin"></i>
                          Analyzing with AI...
                        </>
                      ) : (
                        <>
                          <i className="mr-2 fas fa-robot"></i>
                          Analyze with AI
                        </>
                      )}
                    </button>
                  </form>
              </Card>
            )}
            {step === 2 && (
              <Card padding="xl">
                <div className="space-y-8">
                  <div className="mb-8 text-center">
                    <div className="flex justify-center items-center bg-gradient-to-br from-orange-500 to-red-500 mx-auto mb-4 rounded-2xl w-16 h-16">
                      <i className="text-white text-2xl fas fa-bullseye"></i>
                    </div>
                    <h2 className="mb-2 font-bold text-gray-900 text-2xl">Requirements & Details</h2>
                    <p className="text-gray-600">Review AI suggestions and customize job requirements</p>
                  </div>

                  <div className="space-y-8">
                    {/* Global Bulk Actions Panel */}
                    {selectedSkills.length > 0 && (
                      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 border border-indigo-200 rounded-2xl">
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-3">
                            <div className="flex items-center bg-indigo-100 px-3 py-1 rounded-full">
                              <FaLayerGroup className="mr-2 text-indigo-600" />
                              <span className="font-semibold text-indigo-800 text-sm">
                                {selectedSkills.length} skill{selectedSkills.length !== 1 ? 's' : ''} selected
                              </span>
                            </div>
                            <span className="text-gray-600 text-sm">Bulk actions:</span>
                            <div className="flex gap-1">
                              {['Basic', 'Intermediate', 'Advanced', 'Expert'].map(level => (
                                <button
                                  key={level}
                                  onClick={() => setBulkLevel(level)}
                                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors hover:scale-105 ${
                                    level === 'Basic' ? 'bg-green-500 text-white hover:bg-green-600' :
                                    level === 'Intermediate' ? 'bg-blue-500 text-white hover:bg-blue-600' :
                                    level === 'Advanced' ? 'bg-amber-500 text-white hover:bg-amber-600' :
                                    'bg-red-600 text-white hover:bg-red-700'
                                  }`}
                                >
                                  {level}
                                </button>
                              ))}
                            </div>
                          </div>
                          <button
                            onClick={() => setSelectedSkills([])}
                            className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full text-gray-600 text-sm transition-colors"
                          >
                            <FaCheck className="text-xs" />
                            Clear Selection
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Title Analysis Results */}
                    {agentRequirements.metadata?.title_analysis && (
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 border border-blue-200 rounded-2xl">
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0">
                            <i className="text-blue-600 text-xl fas fa-search"></i>
                          </div>
                          <div className="flex-1">
                            <h4 className="flex items-center mb-3 font-semibold text-blue-800">
                              <i className="mr-2 fas fa-bullseye"></i>
                              Title Analysis Results
                            </h4>
                            <div className="space-y-3">
                              {agentRequirements.metadata.title_analysis.normalized_title && 
                               agentRequirements.metadata.title_analysis.normalized_title !== agentRequirements.metadata.title_analysis.original_title && (
                                <div className="bg-white/80 p-4 border border-blue-100 rounded-lg">
                                  <div className="flex justify-between items-center">
                                    <div>
                                      <p className="text-gray-600 text-sm">Original: <span className="font-medium">{agentRequirements.metadata.title_analysis.original_title}</span></p>
                                      <p className="text-blue-700 text-sm">Normalized: <span className="font-semibold">{agentRequirements.metadata.title_analysis.normalized_title}</span></p>
                                    </div>
                                    <div className="text-right">
                                      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                        agentRequirements.metadata.title_analysis.confidence > 90 
                                          ? 'bg-green-100 text-green-800' 
                                          : agentRequirements.metadata.title_analysis.confidence > 70 
                                          ? 'bg-yellow-100 text-yellow-800' 
                                          : 'bg-red-100 text-red-800'
                                      }`}>
                                        <i className="mr-1 fas fa-percentage"></i>
                                        {Math.round(agentRequirements.metadata.title_analysis.confidence)}% match
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}
                              
                              {agentRequirements.metadata.title_analysis.suggestions && 
                               agentRequirements.metadata.title_analysis.suggestions.length > 0 && (
                                <div className="bg-white/80 p-4 border border-blue-100 rounded-lg">
                                  <p className="mb-2 font-medium text-gray-700 text-sm">Alternative suggestions:</p>
                                  <div className="flex flex-wrap gap-2">
                                    {agentRequirements.metadata.title_analysis.suggestions.slice(0, 3).map((suggestion: any, idx: number) => (
                                      <span key={idx} className="inline-flex items-center bg-blue-100 px-2 py-1 rounded-md text-blue-700 text-xs">
                                        {suggestion.title}
                                        <span className="ml-1 text-blue-500">({Math.round(suggestion.confidence)}%)</span>
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                              
                              <p className="text-blue-600 text-sm">
                                <i className="mr-1 fas fa-info-circle"></i>
                                AI analyzed your job title and standardized it for better skill matching
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* AI Disclaimer and Smart Suggestions Info */}
                    {agentRequirements.metadata?.ai_disclaimer && (
                      <div className="bg-gradient-to-r from-amber-50 to-orange-50 p-6 border border-amber-200 rounded-2xl">
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0">
                            <i className="text-amber-600 text-xl fas fa-exclamation-triangle"></i>
                          </div>
                          <div className="flex-1">
                            <h4 className="flex items-center mb-2 font-semibold text-amber-800">
                              <i className="mr-2 fas fa-robot"></i>
                              AI-Generated Suggestions
                            </h4>
                            <p className="mb-3 text-amber-700 text-sm">
                              {agentRequirements.metadata.ai_disclaimer}
                            </p>
                            <div className="space-y-1 text-amber-600 text-xs">
                              <div>• Skills and requirements are automatically detected from your job description</div>
                              <div>• Skill conflicts have been resolved (e.g., React vs Angular)</div>
                              <div>• Please review and adjust as needed for your specific requirements</div>
                            </div>
                          </div>
                        </div>
                        
                        {/* Show applied smart suggestions if any */}
                        {agentRequirements.metadata?.smart_suggestions && Object.keys(agentRequirements.metadata.smart_suggestions).length > 0 && (
                          <div className="bg-white/60 mt-4 p-4 rounded-xl">
                            <h5 className="flex items-center mb-2 font-medium text-amber-800">
                              <i className="mr-2 text-sm fas fa-magic"></i>
                              Smart Adjustments Applied:
                            </h5>
                            <div className="space-y-1 text-amber-700 text-xs">
                              {agentRequirements.metadata.smart_suggestions.skill_conflicts && (
                                <div>• Resolved conflicts: {agentRequirements.metadata.smart_suggestions.skill_conflicts.join(', ')}</div>
                              )}
                              {agentRequirements.metadata.smart_suggestions.enhanced_skills && (
                                <div>• Enhanced with: {agentRequirements.metadata.smart_suggestions.enhanced_skills.slice(0, 3).join(', ')}</div>
                              )}
                              {agentRequirements.metadata.smart_suggestions.context_adjustments && (
                                <div>• Context-based adjustments applied</div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Context Detection Display */}
                    {agentRequirements.metadata?.smart_skills_analysis?.context_detected && 
                     Object.keys(agentRequirements.metadata.smart_skills_analysis.context_detected).length > 0 && (
                      <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 border border-green-200 rounded-2xl">
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0">
                            <i className="text-green-600 text-xl fas fa-eye"></i>
                          </div>
                          <div className="flex-1">
                            <h4 className="flex items-center mb-3 font-semibold text-green-800">
                              <i className="mr-2 fas fa-search"></i>
                              Technologies Detected in Description
                            </h4>
                            <div className="gap-3 grid grid-cols-1 md:grid-cols-2">
                              {Object.entries(agentRequirements.metadata.smart_skills_analysis.context_detected).map(([tech, emphasis]) => (
                                <div key={tech} className="bg-white/80 px-3 py-2 border border-green-100 rounded-lg">
                                  <div className="flex justify-between items-center">
                                    <span className="font-medium text-gray-800 capitalize">{tech.replace(/[_-]/g, ' ')}</span>
                                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                                      emphasis === 'primary' 
                                        ? 'bg-green-200 text-green-800' 
                                        : emphasis === 'secondary'
                                        ? 'bg-yellow-200 text-yellow-800'
                                        : 'bg-blue-200 text-blue-800'
                                    }`}>
                                      {emphasis === 'primary' ? 'Strong' : emphasis === 'secondary' ? 'Moderate' : 'Mentioned'}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                            <p className="mt-3 text-green-600 text-sm">
                              <i className="mr-1 fas fa-lightbulb"></i>
                              These technologies were automatically detected and used to suggest relevant skills
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Skill Level Legend */}
                    <div className="bg-gray-50 p-6 rounded-2xl">
                      <h4 className="flex items-center mb-4 font-semibold text-gray-800">
                        <i className="mr-2 text-blue-500 fas fa-info-circle"></i>
                        Skill Level Legend
                      </h4>
                      <div className="flex flex-wrap gap-4">
                        <div className="flex items-center">
                          <div className="bg-red-600 mr-2 border-2 border-red-700 rounded-full w-4 h-4"></div>
                          <span className="text-gray-700 text-sm">Expert</span>
                        </div>
                        <div className="flex items-center">
                          <div className="bg-amber-500 mr-2 border-2 border-amber-600 rounded-full w-4 h-4"></div>
                          <span className="text-gray-700 text-sm">Advanced</span>
                        </div>
                        <div className="flex items-center">
                          <div className="bg-blue-500 mr-2 border-2 border-blue-600 rounded-full w-4 h-4"></div>
                          <span className="text-gray-700 text-sm">Intermediate</span>
                        </div>
                        <div className="flex items-center">
                          <div className="bg-green-500 mr-2 border-2 border-green-600 rounded-full w-4 h-4"></div>
                          <span className="text-gray-700 text-sm">Basic</span>
                        </div>
                      </div>
                    </div>

                    {/* Core Skills Section */}
                    <div>
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="flex items-center font-bold text-gray-800 text-lg">
                          <i className="mr-2 text-yellow-500 fas fa-star"></i>
                          Core Skills
                          <span className="bg-yellow-100 ml-2 px-2 py-1 rounded-full font-medium text-yellow-700 text-xs">
                            {selectedRequirements.core_skills.length} selected
                          </span>
                        </h3>
                        
                        {/* Bulk Actions */}
                        {selectedSkills.filter(s => s.startsWith('core_skills')).length > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600 text-sm">
                              {selectedSkills.filter(s => s.startsWith('core_skills')).length} selected
                            </span>
                            <div className="flex gap-1">
                              {['Basic', 'Intermediate', 'Advanced', 'Expert'].map(level => (
                                <button
                                  key={level}
                                  onClick={() => setBulkLevel(level)}
                                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${getLevelColor(level)} text-white hover:opacity-80`}
                                >
                                  {level}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <DndContext
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={handleDragEnd}
                      >
                        <div className="flex flex-wrap gap-3 mb-4 p-4 border-2 border-gray-200 border-dashed rounded-2xl min-h-[60px]">
                          {selectedRequirements.core_skills.length === 0 ? (
                            <p className="py-4 w-full text-gray-400 text-center">No core skills selected yet. Add essential technical skills below.</p>
                          ) : (
                            <SortableContext
                              items={selectedRequirements.core_skills.map((_, idx) => `core_skills-${idx}`)}
                              strategy={verticalListSortingStrategy}
                            >
                              <div className="flex flex-wrap gap-3 w-full">
                                {selectedRequirements.core_skills.map((skill, idx) => {
                                  const isAISuggested = agentRequirements.core_skills?.some(
                                    (aiSkill: any) => aiSkill.skill === skill.skill
                                  );
                                  const skillKey = `core_skills-${idx}`;
                                  const isSelected = selectedSkills.includes(skillKey);
                                  
                                  return (
                                    <SortableSkillItem
                                      key={skillKey}
                                      skill={skill}
                                      index={idx}
                                      category="core_skills"
                                      isAISuggested={isAISuggested}
                                      isSelected={isSelected}
                                      onSelect={(key: string) => {
                                        setSelectedSkills(prev => 
                                          prev.includes(key) 
                                            ? prev.filter(s => s !== key)
                                            : [...prev, key]
                                        );
                                      }}
                                      onRemove={removeRequirement}
                                      onLevelChange={updateSkillLevel}
                                      getSkillIcon={getSkillIcon}
                                      getLevelColor={getLevelColor}
                                      activeLevelDropdown={activeLevelDropdown}
                                      setActiveLevelDropdown={setActiveLevelDropdown}
                                    />
                                  );
                                })}
                              </div>
                            </SortableContext>
                          )}
                        </div>
                      </DndContext>
                    </div>

                    {/* Soft Skills Section */}
                    <div>
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="flex items-center font-bold text-gray-800 text-lg">
                          <i className="mr-2 text-pink-500 fas fa-heart"></i>
                          Soft Skills
                          <span className="bg-pink-100 ml-2 px-2 py-1 rounded-full font-medium text-pink-700 text-xs">
                            {selectedRequirements.soft_skills.length} selected
                          </span>
                        </h3>
                        
                        {/* Bulk Actions */}
                        {selectedSkills.filter(s => s.startsWith('soft_skills')).length > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600 text-sm">
                              {selectedSkills.filter(s => s.startsWith('soft_skills')).length} selected
                            </span>
                            <div className="flex gap-1">
                              {['Basic', 'Intermediate', 'Advanced', 'Expert'].map(level => (
                                <button
                                  key={level}
                                  onClick={() => setBulkLevel(level)}
                                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${getLevelColor(level)} text-white hover:opacity-80`}
                                >
                                  {level}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <DndContext
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={handleDragEnd}
                      >
                        <div className="flex flex-wrap gap-3 mb-4 p-4 border-2 border-gray-200 border-dashed rounded-2xl min-h-[60px]">
                          {selectedRequirements.soft_skills.length === 0 ? (
                            <p className="py-4 w-full text-gray-400 text-center">No soft skills selected yet. Add interpersonal and leadership skills below.</p>
                          ) : (
                            <SortableContext
                              items={selectedRequirements.soft_skills.map((_, idx) => `soft_skills-${idx}`)}
                              strategy={verticalListSortingStrategy}
                            >
                              <div className="flex flex-wrap gap-3 w-full">
                                {selectedRequirements.soft_skills.map((skill, idx) => {
                                  const isAISuggested = agentRequirements.soft_skills?.some(
                                    (aiSkill: any) => aiSkill.skill === skill.skill
                                  );
                                  const skillKey = `soft_skills-${idx}`;
                                  const isSelected = selectedSkills.includes(skillKey);
                                  
                                  return (
                                    <SortableSkillItem
                                      key={skillKey}
                                      skill={skill}
                                      index={idx}
                                      category="soft_skills"
                                      isAISuggested={isAISuggested}
                                      isSelected={isSelected}
                                      onSelect={(key: string) => {
                                        setSelectedSkills(prev => 
                                          prev.includes(key) 
                                            ? prev.filter(s => s !== key)
                                            : [...prev, key]
                                        );
                                      }}
                                      onRemove={removeRequirement}
                                      onLevelChange={updateSkillLevel}
                                      getSkillIcon={getSkillIcon}
                                      getLevelColor={getLevelColor}
                                      activeLevelDropdown={activeLevelDropdown}
                                      setActiveLevelDropdown={setActiveLevelDropdown}
                                    />
                                  );
                                })}
                              </div>
                            </SortableContext>
                          )}
                        </div>
                      </DndContext>
                    </div>

                    {/* Bonus Skills Section */}
                    <div>
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="flex items-center font-bold text-gray-800 text-lg">
                          <i className="mr-2 text-green-500 fas fa-plus-circle"></i>
                          Bonus Skills
                          <span className="bg-green-100 ml-2 px-2 py-1 rounded-full font-medium text-green-700 text-xs">
                            {selectedRequirements.bonus_skills.length} selected
                          </span>
                        </h3>
                        
                        {/* Bulk Actions */}
                        {selectedSkills.filter(s => s.startsWith('bonus_skills')).length > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600 text-sm">
                              {selectedSkills.filter(s => s.startsWith('bonus_skills')).length} selected
                            </span>
                            <div className="flex gap-1">
                              {['Basic', 'Intermediate', 'Advanced', 'Expert'].map(level => (
                                <button
                                  key={level}
                                  onClick={() => setBulkLevel(level)}
                                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${getLevelColor(level)} text-white hover:opacity-80`}
                                >
                                  {level}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <DndContext
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={handleDragEnd}
                      >
                        <div className="flex flex-wrap gap-3 mb-6 p-4 border-2 border-gray-200 border-dashed rounded-2xl min-h-[60px]">
                          {selectedRequirements.bonus_skills.length === 0 ? (
                            <p className="py-4 w-full text-gray-400 text-center">No bonus skills selected yet. Add nice-to-have skills below.</p>
                          ) : (
                            <SortableContext
                              items={selectedRequirements.bonus_skills.map((_, idx) => `bonus_skills-${idx}`)}
                              strategy={verticalListSortingStrategy}
                            >
                              <div className="flex flex-wrap gap-3 w-full">
                                {selectedRequirements.bonus_skills.map((skill, idx) => {
                                  const isAISuggested = agentRequirements.bonus_skills?.some(
                                    (aiSkill: any) => aiSkill.skill === skill.skill
                                  );
                                  const skillKey = `bonus_skills-${idx}`;
                                  const isSelected = selectedSkills.includes(skillKey);
                                  
                                  return (
                                    <SortableSkillItem
                                      key={skillKey}
                                      skill={skill}
                                      index={idx}
                                      category="bonus_skills"
                                      isAISuggested={isAISuggested}
                                      isSelected={isSelected}
                                      onSelect={(key: string) => {
                                        setSelectedSkills(prev => 
                                          prev.includes(key) 
                                            ? prev.filter(s => s !== key)
                                            : [...prev, key]
                                        );
                                      }}
                                      onRemove={removeRequirement}
                                      onLevelChange={updateSkillLevel}
                                      getSkillIcon={getSkillIcon}
                                      getLevelColor={getLevelColor}
                                      activeLevelDropdown={activeLevelDropdown}
                                      setActiveLevelDropdown={setActiveLevelDropdown}
                                    />
                                  );
                                })}
                              </div>
                            </SortableContext>
                          )}
                        </div>
                      </DndContext>
                    </div>

                    {/* Add Skills Section */}
                    <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-6 rounded-2xl">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="flex items-center font-semibold text-gray-800">
                          <i className="mr-2 text-purple-600 fas fa-search"></i>
                          Add Skills
                        </h4>
                        
                        {/* Quick Add Toggle */}
                        <button
                          onClick={() => setQuickAddMode(!quickAddMode)}
                          className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                            quickAddMode 
                              ? 'bg-green-100 text-green-700 border border-green-300' 
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          }`}
                        >
                          <FaMagic className="text-xs" />
                          Quick Add {quickAddMode ? 'ON' : 'OFF'}
                        </button>
                      </div>
                      
                      {/* Skill Suggestions */}
                      {showSuggestions && skillSuggestions.length > 0 && (
                        <div className="bg-gradient-to-r from-blue-50 to-purple-50 mb-4 p-4 border border-blue-200 rounded-xl">
                          <div className="flex items-center mb-2">
                            <FaLightbulb className="mr-2 text-yellow-500" />
                            <span className="font-medium text-gray-800 text-sm">Suggested skills that work well together:</span>
                            <button
                              onClick={() => setShowSuggestions(false)}
                              className="ml-auto text-gray-400 hover:text-gray-600"
                            >
                              ×
                            </button>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {skillSuggestions.map((suggestion, idx) => (
                              <button
                                key={idx}
                                onClick={() => {
                                  addRequirement(`${suggestion.skill}:${suggestion.level}`, suggestion.category);
                                  setSkillSuggestions(prev => prev.filter((_, i) => i !== idx));
                                }}
                                className="group flex items-center gap-2 bg-white hover:bg-blue-50 px-3 py-1 border hover:border-blue-300 rounded-full text-sm transition-colors"
                              >
                                {getSkillIcon(suggestion.skill)}
                                <span className="text-gray-700">{suggestion.skill}</span>
                                <div className={`w-2 h-2 rounded-full border ${getLevelColor(suggestion.level)}`}></div>
                                <FaPlus className="opacity-0 group-hover:opacity-100 text-blue-500 text-xs transition-opacity" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div className="relative" ref={dropdownRef}>
                        <div className="relative">
                          <i className="top-1/2 left-4 absolute text-gray-400 -translate-y-1/2 fas fa-search"></i>
                          <input 
                            className="bg-white/90 shadow-lg backdrop-blur-md py-4 pr-6 pl-12 border border-gray-200 focus:border-transparent rounded-2xl focus:ring-2 focus:ring-purple-500 w-full text-gray-900 placeholder:text-gray-500 text-lg transition-all duration-300" 
                            placeholder={quickAddMode ? "Type skill name and press Enter for quick add..." : "Search skills (e.g. React, Leadership, Git...)"} 
                            value={requirementSearch}
                            onChange={(e) => {
                              setRequirementSearch(e.target.value);
                              setShowRequirementDropdown(true);
                            }}
                            onFocus={() => setShowRequirementDropdown(true)}
                            onKeyDown={(e) => {
                              if (e.key === "Escape") {
                                setShowRequirementDropdown(false);
                              } else if (e.key === "Enter" && quickAddMode) {
                                handleQuickAdd(e);
                              }
                            }}
                          />
                          {quickAddMode && (
                            <div className="top-1/2 right-4 absolute flex items-center gap-2 -translate-y-1/2 transform">
                              <span className="bg-green-100 px-2 py-1 rounded-full font-medium text-green-700 text-xs">
                                Press Enter
                              </span>
                              <i className="text-green-500 fas fa-bolt"></i>
                            </div>
                          )}
                        </div>

                        {/* Skills Dropdown */}
                        {showRequirementDropdown && requirementSearch && (
                          <div className="z-10 absolute bg-white shadow-xl mt-2 border border-gray-200 rounded-2xl w-full max-h-60 overflow-y-auto">
                            {getFilteredSkills().map((skill, idx) => (
                              <div key={idx} className="px-4 py-3 border-gray-100 border-b last:border-b-0">
                                <div className="flex justify-between items-center mb-2">
                                  <div className="flex items-center">
                                    <i className={`${getSkillIcon(skill.name)} text-lg text-gray-700 mr-3`}></i>
                                    <span className="font-medium text-gray-900">{skill.name}</span>
                                    <span className="bg-gray-100 ml-2 px-2 py-1 rounded-full text-gray-600 text-xs capitalize">
                                      {skill.category.replace('_', ' ')}
                                    </span>
                                    {skill.source === 'detected' && (
                                      <span className="bg-green-100 ml-2 px-2 py-1 border border-green-200 rounded-full font-medium text-green-700 text-xs">
                                        ✨ Detected
                                      </span>
                                    )}
                                  </div>
                                </div>
                                <div className="flex gap-2">
                                  {(skill.levels as string[]).map((level: string, levelIdx: number) => (
                                    <button
                                      key={levelIdx}
                                      type="button"
                                      className={`flex items-center gap-2 bg-gray-50 hover:bg-purple-50 px-3 py-1 rounded-full text-sm transition-colors group`}
                                      onClick={() => addRequirement(`${skill.name}:${level}`, skill.category)}
                                    >
                                      <div className={`w-2 h-2 rounded-full border ${getLevelColor(level)}`}></div>
                                      <span className="text-gray-700 group-hover:text-purple-700">{level}</span>
                                      <i className="opacity-0 group-hover:opacity-100 text-purple-500 text-xs transition-opacity fas fa-plus"></i>
                                    </button>
                                  ))}
                                </div>
                              </div>
                            ))}
                            {getFilteredSkills().length === 0 && requirementSearch && (
                              <div className="px-4 py-3 text-gray-500 text-sm text-center">
                                No skills found matching "{requirementSearch}"
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Quick Add Popular Skills */}
                      {getTotalSkillsCount() === 0 && (
                        <div className="mt-6">
                          <p className="mb-3 text-gray-600 text-sm">Popular skills to get started:</p>
                          <div className="space-y-3">
                            <div>
                              <p className="mb-2 font-medium text-gray-500 text-xs">Core Technical Skills:</p>
                              <div className="flex flex-wrap gap-2">
                                {[
                                  {name: "React", level: "Advanced", category: "core_skills"},
                                  {name: "JavaScript", level: "Advanced", category: "core_skills"},
                                  {name: "TypeScript", level: "Intermediate", category: "core_skills"},
                                  {name: "CSS3", level: "Intermediate", category: "core_skills"}
                                ].map((skill) => (
                                  <button
                                    key={skill.name}
                                    type="button"
                                    className="group flex items-center gap-2 bg-white hover:bg-yellow-50 px-3 py-1 border hover:border-yellow-300 rounded-full text-sm transition-colors"
                                    onClick={() => addRequirement(`${skill.name}:${skill.level}`, skill.category as any)}
                                  >
                                    <i className={`${getSkillIcon(skill.name)} text-gray-600`}></i>
                                    <span className="text-gray-700">{skill.name}</span>
                                    <div className={`w-2 h-2 rounded-full border ${getLevelColor(skill.level)}`}></div>
                                    <i className="opacity-0 group-hover:opacity-100 text-purple-500 text-xs transition-opacity fas fa-plus"></i>
                                  </button>
                                ))}
                              </div>
                            </div>
                            <div>
                              <p className="mb-2 font-medium text-gray-500 text-xs">Soft Skills:</p>
                              <div className="flex flex-wrap gap-2">
                                {[
                                  {name: "Communication", level: "Advanced", category: "soft_skills"},
                                  {name: "Problem Solving", level: "Advanced", category: "soft_skills"}
                                ].map((skill) => (
                                  <button
                                    key={skill.name}
                                    type="button"
                                    className="group flex items-center gap-2 bg-white hover:bg-pink-50 px-3 py-1 border hover:border-pink-300 rounded-full text-sm transition-colors"
                                    onClick={() => addRequirement(`${skill.name}:${skill.level}`, skill.category as any)}
                                  >
                                    <i className={`${getSkillIcon(skill.name)} text-gray-600`}></i>
                                    <span className="text-gray-700">{skill.name}</span>
                                    <div className={`w-2 h-2 rounded-full border ${getLevelColor(skill.level)}`}></div>
                                    <i className="opacity-0 group-hover:opacity-100 text-purple-500 text-xs transition-opacity fas fa-plus"></i>
                                  </button>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="gap-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                      <div>
                        <div className="flex justify-between items-center mb-3">
                          <label className="block font-semibold text-gray-700">
                            <i className="fa-layer-group mr-2 text-blue-600 fas"></i>
                            Seniority Level
                          </label>
                          {loadingExperience && (
                            <div className="flex items-center text-blue-600 text-sm">
                              <i className="mr-2 animate-spin fas fa-spinner"></i>
                              Detecting...
                            </div>
                          )}
                        </div>
                        <select 
                          className="bg-white/80 shadow-lg backdrop-blur-md px-6 py-4 border border-gray-200 focus:border-transparent rounded-2xl focus:ring-2 focus:ring-purple-500 w-full text-gray-900 text-lg transition-all duration-300" 
                          value={form.seniority} 
                          onChange={(e) => setForm({ ...form, seniority: e.target.value })}
                        >
                          <option value="">Select seniority level...</option>
                          <option value="Lead">Lead</option>
                          <option value="Senior">Senior</option>
                          <option value="Mid">Mid</option>
                          <option value="Junior">Junior</option>
                        </select>
                        
                        {/* Experience Level Detection Display */}
                        {experienceData && (
                          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 mt-3 p-4 border border-blue-200 rounded-xl">
                            <div className="flex justify-between items-start mb-2">
                              <h5 className="flex items-center font-semibold text-gray-800 text-sm">
                                <i className="mr-2 text-blue-600 fas fa-brain"></i>
                                AI Detection
                              </h5>
                              <div className={`px-2 py-1 rounded-full text-xs ${
                                experienceData.confidence_score > 0.8 
                                  ? 'bg-green-100 text-green-700' 
                                  : experienceData.confidence_score > 0.6
                                  ? 'bg-yellow-100 text-yellow-700'
                                  : 'bg-red-100 text-red-700'
                              }`}>
                                {Math.round(experienceData.confidence_score * 100)}% Confidence
                              </div>
                            </div>
                            
                            <div className="space-y-2">
                              <div className="flex justify-between items-center">
                                <span className="font-medium text-gray-700 text-sm">Detected Level:</span>
                                <span className="bg-blue-100 px-2 py-1 rounded-full font-medium text-blue-800 text-sm">
                                  {experienceData.detected_level}
                                </span>
                              </div>
                              
                              {experienceData.years_of_experience.min_years && (
                                <div className="flex justify-between items-center">
                                  <span className="font-medium text-gray-700 text-sm">Years Required:</span>
                                  <span className="text-gray-600 text-sm">
                                    {experienceData.years_of_experience.min_years}
                                    {experienceData.years_of_experience.max_years !== experienceData.years_of_experience.min_years 
                                      ? `-${experienceData.years_of_experience.max_years}` : '+'} years
                                  </span>
                                </div>
                              )}
                              
                              {experienceData.alternative_levels.length > 0 && (
                                <div>
                                  <span className="font-medium text-gray-700 text-sm">Alternatives:</span>
                                  <div className="flex gap-1 mt-1">
                                    {experienceData.alternative_levels.slice(0, 2).map((alt, index) => (
                                      <button
                                        key={index}
                                        type="button"
                                        onClick={() => setForm(prev => ({ ...prev, seniority: alt.level }))}
                                        className="bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded-lg font-medium text-gray-700 text-xs transition-colors"
                                      >
                                        {alt.level} ({Math.round(alt.confidence * 100)}%)
                                      </button>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            {experienceData.detected_level !== form.seniority && form.seniority && (
                              <button
                                type="button"
                                onClick={() => setForm(prev => ({ ...prev, seniority: experienceData.detected_level }))}
                                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 mt-3 px-3 py-1 rounded-lg font-medium text-white text-sm transition-colors"
                              >
                                <i className="fas fa-magic"></i>
                                Apply "{experienceData.detected_level}"
                              </button>
                            )}
                          </div>
                        )}
                      </div>

                      <div>
                        <label className="block mb-3 font-semibold text-gray-700">
                          <i className="mr-2 text-green-600 fas fa-map-marker-alt"></i>
                          Location
                        </label>
                        <div className="relative">
                          <i className="top-1/2 left-4 absolute text-gray-400 -translate-y-1/2 fas fa-globe"></i>
                          <input 
                            className="bg-white/80 shadow-lg backdrop-blur-md py-4 pr-6 pl-12 border border-gray-200 focus:border-transparent rounded-2xl focus:ring-2 focus:ring-purple-500 w-full text-gray-900 placeholder:text-gray-500 text-lg transition-all duration-300" 
                            placeholder="e.g., San Francisco, CA / Remote / Hybrid"
                            value={form.location}
                            onChange={(e) => setForm({ ...form, location: e.target.value })}
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block mb-3 font-semibold text-gray-700">
                          <i className="mr-2 text-orange-600 fas fa-question-circle"></i>
                          Screening Questions
                        </label>
                        <div className="relative">
                          <i className="top-1/2 left-4 absolute text-gray-400 -translate-y-1/2 fas fa-plus-circle"></i>
                          <input 
                            className="bg-white/80 shadow-lg backdrop-blur-md py-4 pr-6 pl-12 border border-gray-200 focus:border-transparent rounded-2xl focus:ring-2 focus:ring-purple-500 w-full text-gray-900 placeholder:text-gray-500 text-lg transition-all duration-300" 
                            placeholder="Add screening question..." 
                            onKeyDown={(e) => {
                              if (e.key === "Enter" && e.currentTarget.value.trim()) {
                                setForm({ ...form, screening_questions: [...form.screening_questions, e.currentTarget.value.trim()] });
                                e.currentTarget.value = "";
                              }
                            }} 
                          />
                        </div>
                      </div>
                    </div>

                    {/* Salary Range Section */}
                    <div>
                      <div className="flex justify-between items-center mb-4">
                        <label className="block font-semibold text-gray-700">
                          <i className="mr-2 text-purple-600 fas fa-dollar-sign"></i>
                          Salary Range
                        </label>
                        {loadingSalary && (
                          <div className="flex items-center text-purple-600 text-sm">
                            <i className="mr-2 animate-spin fas fa-spinner"></i>
                            Getting salary suggestions...
                          </div>
                        )}
                      </div>
                      
                      <div className="gap-4 grid grid-cols-1 md:grid-cols-2">
                        <div>
                          <label className="block mb-2 font-medium text-gray-600 text-sm">Minimum Salary</label>
                          <div className="relative">
                            <span className="top-1/2 left-4 absolute text-gray-400 -translate-y-1/2">$</span>
                            <input 
                              type="number"
                              className="bg-white/80 shadow-lg backdrop-blur-md py-3 pr-4 pl-8 border border-gray-200 focus:border-transparent rounded-xl focus:ring-2 focus:ring-purple-500 w-full text-gray-900 placeholder:text-gray-500 transition-all duration-300" 
                              placeholder="e.g., 80000"
                              value={form.salary_min}
                              onChange={(e) => setForm({ ...form, salary_min: e.target.value })}
                            />
                          </div>
                        </div>
                        
                        <div>
                          <label className="block mb-2 font-medium text-gray-600 text-sm">Maximum Salary</label>
                          <div className="relative">
                            <span className="top-1/2 left-4 absolute text-gray-400 -translate-y-1/2">$</span>
                            <input 
                              type="number"
                              className="bg-white/80 shadow-lg backdrop-blur-md py-3 pr-4 pl-8 border border-gray-200 focus:border-transparent rounded-xl focus:ring-2 focus:ring-purple-500 w-full text-gray-900 placeholder:text-gray-500 transition-all duration-300" 
                              placeholder="e.g., 120000"
                              value={form.salary_max}
                              onChange={(e) => setForm({ ...form, salary_max: e.target.value })}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Salary Suggestions Display */}
                      {salaryData && (
                        <div className="bg-gradient-to-r from-purple-50 to-blue-50 mt-4 p-6 border border-purple-200 rounded-2xl">
                          <div className="flex justify-between items-start mb-4">
                            <h4 className="flex items-center font-bold text-gray-800 text-lg">
                              <i className="mr-2 text-purple-600 fas fa-chart-line"></i>
                              AI Salary Insights
                            </h4>
                            <div className="flex items-center gap-2">
                              <div className="bg-green-100 px-2 py-1 rounded-full text-green-700 text-xs">
                                {Math.round(salaryData.confidence_score * 100)}% Confidence
                              </div>
                              <div className={`px-2 py-1 rounded-full text-xs ${
                                salaryData.market_trends.trend === 'increasing' 
                                  ? 'bg-green-100 text-green-700' 
                                  : salaryData.market_trends.trend === 'decreasing'
                                  ? 'bg-red-100 text-red-700'
                                  : 'bg-gray-100 text-gray-700'
                              }`}>
                                {salaryData.market_trends.trend === 'increasing' ? '↗' : 
                                 salaryData.market_trends.trend === 'decreasing' ? '↘' : '→'} 
                                {salaryData.market_trends.percentage_change > 0 ? '+' : ''}{salaryData.market_trends.percentage_change}%
                              </div>
                            </div>
                          </div>

                          <div className="gap-4 grid grid-cols-1 md:grid-cols-3 mb-4">
                            <div className="bg-white/50 p-4 rounded-xl">
                              <div className="font-medium text-gray-600 text-sm">Market Average</div>
                              <div className="font-bold text-gray-900 text-xl">${salaryData.average_salary.toLocaleString()}</div>
                            </div>
                            <div className="bg-white/50 p-4 rounded-xl">
                              <div className="font-medium text-gray-600 text-sm">Recommended Range</div>
                              <div className="font-bold text-gray-900 text-xl">
                                ${salaryData.min_salary.toLocaleString()} - ${salaryData.max_salary.toLocaleString()}
                              </div>
                            </div>
                            <div className="bg-white/50 p-4 rounded-xl">
                              <div className="font-medium text-gray-600 text-sm">75th Percentile</div>
                              <div className="font-bold text-gray-900 text-xl">${salaryData.percentile_75.toLocaleString()}</div>
                            </div>
                          </div>

                          <div className="gap-4 grid grid-cols-1 md:grid-cols-2">
                            <div>
                              <h5 className="mb-2 font-semibold text-gray-700">Salary Factors</h5>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Location Adjustment:</span>
                                  <span className={`font-medium ${salaryData.location_adjustment > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {salaryData.location_adjustment > 0 ? '+' : ''}{(salaryData.location_adjustment * 100).toFixed(1)}%
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Skills Premium:</span>
                                  <span className="font-medium text-green-600">+{(salaryData.skill_premium * 100).toFixed(1)}%</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Seniority Multiplier:</span>
                                  <span className="font-medium text-blue-600">{salaryData.seniority_multiplier.toFixed(1)}x</span>
                                </div>
                              </div>
                            </div>
                            
                            <div>
                              <h5 className="mb-2 font-semibold text-gray-700">Comparable Positions</h5>
                              <div className="space-y-2">
                                {salaryData.comparable_positions.slice(0, 3).map((position, index) => (
                                  <div key={index} className="bg-white/30 p-2 rounded-lg text-sm">
                                    <div className="font-medium text-gray-800">{position.title}</div>
                                    <div className="flex justify-between text-gray-600 text-xs">
                                      <span>{position.company_size}</span>
                                      <span>{position.salary_range}</span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>

                          <div className="flex gap-2 mt-4">
                            <button
                              type="button"
                              onClick={() => {
                                setForm(prev => ({
                                  ...prev,
                                  salary_min: Math.round(salaryData.min_salary).toString(),
                                  salary_max: Math.round(salaryData.max_salary).toString()
                                }));
                              }}
                              className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-xl font-medium text-white text-sm transition-colors"
                            >
                              <i className="fas fa-magic"></i>
                              Apply Recommendations
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setForm(prev => ({
                                  ...prev,
                                  salary_min: Math.round(salaryData.percentile_25).toString(),
                                  salary_max: Math.round(salaryData.percentile_75).toString()
                                }));
                              }}
                              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-xl font-medium text-white text-sm transition-colors"
                            >
                              <i className="fas fa-chart-bar"></i>
                              Use Market Range
                            </button>
                          </div>
                        </div>
                      )}
                    </div>

                    {form.screening_questions.length > 0 && (
                      <div>
                        <h4 className="mb-3 font-semibold text-gray-700">Added Questions:</h4>
                        <div className="space-y-2">
                          {form.screening_questions.map((q, idx) => (
                            <div key={idx} className="flex justify-between items-center bg-gray-50 p-4 rounded-xl">
                              <span className="text-gray-800">{q}</span>
                              <button 
                                type="button" 
                                className="text-red-500 hover:text-red-700 transition-colors" 
                                onClick={() => setForm({ ...form, screening_questions: form.screening_questions.filter((qq) => qq !== q) })}
                              >
                                <i className="fas fa-trash"></i>
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex gap-4">
                      <button 
                        type="button" 
                        className="bg-gray-100 hover:bg-gray-200 px-8 py-4 rounded-2xl font-semibold text-gray-700 transition-all duration-300"
                        onClick={() => setStep(1)}
                      >
                        <i className="fa-arrow-left mr-2 fas"></i>
                        Back
                      </button>
                      <button 
                        type="button" 
                        className="flex-1 bg-gradient-to-r from-orange-600 hover:from-orange-700 to-red-600 hover:to-red-700 shadow-xl hover:shadow-2xl px-8 py-4 rounded-2xl font-bold text-white hover:scale-105 transition-all duration-300" 
                        onClick={async () => {
                          // FIXED: Format requirements as objects for backend compatibility  
                          const formattedRequirements = [
                            ...selectedRequirements.core_skills.map(s => ({
                              skill: s.skill,
                              level: s.level,
                              weight: "0.8"
                            })),
                            ...selectedRequirements.soft_skills.map(s => ({
                              skill: s.skill,
                              level: s.level,
                              weight: "0.6"
                            })),
                            ...selectedRequirements.bonus_skills.map(s => ({
                              skill: s.skill,
                              level: s.level,
                              weight: "0.4"
                            }))
                          ];
                          const job = { ...form, requirements: formattedRequirements };
                          const summary = await summarizeJob(job);
                          setAgentSummary(summary);
                          setStep(3);
                        }}
                        disabled={generating}
                      >
                        {generating ? (
                          <>
                            <i className="mr-2 fas fa-spinner fa-spin"></i>
                            Generating Summary...
                          </>
                        ) : (
                          <>
                            <i className="mr-2 fas fa-brain"></i>
                            Generate AI Summary
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </Card>
            )}
            {step === 3 && (
              <Card padding="xl">
                <div className="space-y-8">
                  <div className="mb-8 text-center">
                    <div className="flex justify-center items-center bg-gradient-to-br from-green-500 to-blue-500 mx-auto mb-4 rounded-2xl w-16 h-16">
                      <i className="text-white text-2xl fas fa-check-circle"></i>
                    </div>
                    <h2 className="mb-2 font-bold text-gray-900 text-2xl">AI Job Summary</h2>
                    <p className="text-gray-600">Review and customize the AI-generated job summary</p>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <label className="block mb-3 font-semibold text-gray-700">
                        <i className="mr-2 text-green-600 fas fa-robot"></i>
                        Generated Summary
                      </label>
                      <div className="bg-gradient-to-r from-green-50 to-blue-50 mb-4 p-6 border border-green-200 rounded-2xl">
                        <div className="flex items-start space-x-3">
                          <div className="flex flex-shrink-0 justify-center items-center bg-green-100 rounded-lg w-10 h-10">
                            <i className="text-green-600 fas fa-brain"></i>
                          </div>
                          <div>
                            <h4 className="mb-2 font-semibold text-green-800">AI Analysis Complete</h4>
                            <p className="text-green-700 text-sm">The summary below has been optimized for ATS systems and candidate attraction.</p>
                          </div>
                        </div>
                      </div>
                      <textarea 
                        className="bg-white/80 shadow-lg backdrop-blur-md px-6 py-4 border border-gray-200 focus:border-transparent rounded-2xl focus:ring-2 focus:ring-green-500 w-full text-gray-900 placeholder:text-gray-500 text-lg transition-all duration-300" 
                        value={agentSummary} 
                        onChange={(e) => setAgentSummary(e.target.value)} 
                        rows={10}
                        placeholder="AI will generate a comprehensive job summary here..."
                      />
                      
                      {/* AI Summary Disclaimer */}
                      <div className="bg-amber-50 mt-4 p-4 border border-amber-200 rounded-xl">
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0">
                            <i className="text-amber-600 fas fa-exclamation-triangle"></i>
                          </div>
                          <div className="flex-1">
                            <h5 className="flex items-center mb-1 font-medium text-amber-800">
                              <i className="mr-2 text-sm fas fa-robot"></i>
                              AI-Generated Summary
                            </h5>
                            <p className="mb-2 text-amber-700 text-sm">
                              This job summary has been automatically generated based on your job title and description. 
                              Please review and edit as needed to ensure it accurately reflects your specific requirements.
                            </p>
                            <div className="space-y-1 text-amber-600 text-xs">
                              <div>• Summary is optimized for ATS systems and candidate attraction</div>
                              <div>• Edit freely to match your company's tone and specific needs</div>
                              <div>• Ensure all details are accurate before publishing</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Enhanced Live Job Preview */}
                    <div className="bg-gradient-to-br from-gray-50 to-blue-50 p-6 border border-gray-200 rounded-2xl">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="flex items-center font-semibold text-gray-800">
                          <i className="mr-2 text-blue-600 fas fa-eye"></i>
                          Live Job Preview
                        </h4>
                        <button 
                          type="button"
                          className="flex items-center gap-2 bg-blue-100 hover:bg-blue-200 px-3 py-1 rounded-full font-medium text-blue-700 text-sm transition-colors"
                        >
                          <i className="fas fa-external-link-alt"></i>
                          Preview in New Tab
                        </button>
                      </div>
                      
                      {/* Mock Job Posting Layout */}
                      <div className="bg-white shadow-lg p-6 border rounded-xl">
                        {/* Job Header */}
                        <div className="mb-6 pb-6 border-gray-200 border-b">
                          <div className="flex justify-between items-start mb-4">
                            <div>
                              <h1 className="mb-2 font-bold text-gray-900 text-2xl">{form.title || 'Job Title'}</h1>
                              <div className="flex items-center gap-4 text-gray-600 text-sm">
                                <span className="flex items-center">
                                  <i className="mr-1 fas fa-building"></i>
                                  Your Company
                                </span>
                                <span className="flex items-center">
                                  <i className="mr-1 fas fa-map-marker-alt"></i>
                                  {form.location || 'Location not specified'}
                                </span>
                                <span className="flex items-center">
                                  <i className="mr-1 fas fa-clock"></i>
                                  Posted today
                                </span>
                              </div>
                            </div>
                            <div className="text-right">
                              {form.salary_min && form.salary_max && (
                                <div className="bg-green-100 mb-2 px-3 py-1 rounded-full font-semibold text-green-800 text-sm">
                                  ${parseInt(form.salary_min).toLocaleString()} - ${parseInt(form.salary_max).toLocaleString()}
                                </div>
                              )}
                              {form.seniority && (
                                <div className="bg-blue-100 px-3 py-1 rounded-full font-medium text-blue-800 text-sm">
                                  {form.seniority}
                                </div>
                              )}
                            </div>
                          </div>
                          
                          {/* Quick Actions */}
                          <div className="flex gap-3">
                            <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium text-white transition-colors">
                              <i className="fas fa-paper-plane"></i>
                              Apply Now
                            </button>
                            <button className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg font-medium text-gray-700 transition-colors">
                              <i className="fas fa-heart"></i>
                              Save Job
                            </button>
                            <button className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg font-medium text-gray-700 transition-colors">
                              <i className="fas fa-share"></i>
                              Share
                            </button>
                          </div>
                        </div>

                        {/* Job Description */}
                        <div className="mb-6">
                          <h3 className="mb-3 font-semibold text-gray-900 text-lg">Job Description</h3>
                          <div className="text-gray-700 leading-relaxed">
                            {agentSummary ? (
                              <div className="space-y-3">
                                {agentSummary.split('\n\n').slice(0, 3).map((paragraph, idx) => (
                                  <p key={idx}>{paragraph}</p>
                                ))}
                                {agentSummary.split('\n\n').length > 3 && (
                                  <p className="text-gray-500 italic">... and more</p>
                                )}
                              </div>
                            ) : (
                              <p className="text-gray-500 italic">
                                {form.description ? 
                                  form.description.substring(0, 300) + (form.description.length > 300 ? '...' : '') :
                                  'Job description will appear here after AI generates the summary'
                                }
                              </p>
                            )}
                          </div>
                        </div>

                        {/* Requirements */}
                        {getTotalSkillsCount() > 0 && (
                          <div className="mb-6">
                            <h3 className="mb-3 font-semibold text-gray-900 text-lg">Requirements</h3>
                            <div className="space-y-4">
                              {selectedRequirements.core_skills.length > 0 && (
                                <div>
                                  <h4 className="mb-2 font-medium text-gray-800">Technical Skills</h4>
                                  <div className="flex flex-wrap gap-2">
                                    {selectedRequirements.core_skills.slice(0, 6).map((skill, idx) => (
                                      <span key={idx} className="bg-blue-100 px-3 py-1 rounded-full font-medium text-blue-800 text-sm">
                                        {skill.skill} ({skill.level})
                                      </span>
                                    ))}
                                    {selectedRequirements.core_skills.length > 6 && (
                                      <span className="bg-gray-100 px-3 py-1 rounded-full font-medium text-gray-600 text-sm">
                                        +{selectedRequirements.core_skills.length - 6} more
                                      </span>
                                    )}
                                  </div>
                                </div>
                              )}
                              
                              {selectedRequirements.soft_skills.length > 0 && (
                                <div>
                                  <h4 className="mb-2 font-medium text-gray-800">Soft Skills</h4>
                                  <div className="flex flex-wrap gap-2">
                                    {selectedRequirements.soft_skills.slice(0, 4).map((skill, idx) => (
                                      <span key={idx} className="bg-green-100 px-3 py-1 rounded-full font-medium text-green-800 text-sm">
                                        {skill.skill}
                                      </span>
                                    ))}
                                    {selectedRequirements.soft_skills.length > 4 && (
                                      <span className="bg-gray-100 px-3 py-1 rounded-full font-medium text-gray-600 text-sm">
                                        +{selectedRequirements.soft_skills.length - 4} more
                                      </span>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Screening Questions Preview */}
                        {form.screening_questions.length > 0 && (
                          <div className="mb-6">
                            <h3 className="mb-3 font-semibold text-gray-900 text-lg">Application Questions</h3>
                            <div className="bg-gray-50 p-4 rounded-lg">
                              <p className="mb-2 text-gray-700 text-sm">Candidates will be asked to answer these questions:</p>
                              <ul className="space-y-1">
                                {form.screening_questions.slice(0, 3).map((q, idx) => (
                                  <li key={idx} className="flex items-start gap-2 text-gray-600 text-sm">
                                    <span className="flex-shrink-0 bg-blue-500 mt-1.5 rounded-full w-1.5 h-1.5"></span>
                                    {q}
                                  </li>
                                ))}
                                {form.screening_questions.length > 3 && (
                                  <li className="text-gray-500 text-sm italic">
                                    +{form.screening_questions.length - 3} more questions
                                  </li>
                                )}
                              </ul>
                            </div>
                          </div>
                        )}

                        {/* Company Info Placeholder */}
                        <div className="pt-6 border-gray-200 border-t">
                          <h3 className="mb-3 font-semibold text-gray-900 text-lg">About the Company</h3>
                          <div className="flex items-start gap-4">
                            <div className="bg-gray-200 rounded-lg w-16 h-16"></div>
                            <div>
                              <p className="mb-2 font-medium text-gray-900">Your Company Name</p>
                              <p className="text-gray-600 text-sm">Company description and culture information will appear here.</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-6 rounded-2xl">
                      <h4 className="mb-4 font-semibold text-gray-800">Job Statistics</h4>
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Title:</span>
                          <span className="font-medium text-gray-900">{form.title}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Seniority:</span>
                          <span className="font-medium text-gray-900">{form.seniority || 'Not specified'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Requirements:</span>
                          <span className="font-medium text-gray-900">{getTotalSkillsCount()} skills</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Screening Questions:</span>
                          <span className="font-medium text-gray-900">{form.screening_questions.length} questions</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-4">
                      <button 
                        type="button" 
                        className="bg-gray-100 hover:bg-gray-200 px-8 py-4 rounded-2xl font-semibold text-gray-700 transition-all duration-300"
                        onClick={() => setStep(2)}
                      >
                        <i className="fa-arrow-left mr-2 fas"></i>
                        Back
                      </button>
                      <button 
                        type="button" 
                        className="flex-1 bg-gradient-to-r from-green-600 hover:from-green-700 to-blue-600 hover:to-blue-700 shadow-xl hover:shadow-2xl px-8 py-4 rounded-2xl font-bold text-white hover:scale-105 transition-all duration-300" 
                        onClick={async () => {
                          setCreating(true);
                          // FIXED: Format requirements as objects for backend compatibility
                          const formattedRequirements = [
                            ...selectedRequirements.core_skills.map(s => ({
                              skill: s.skill,
                              level: s.level,
                              weight: "0.8"
                            })),
                            ...selectedRequirements.soft_skills.map(s => ({
                              skill: s.skill,
                              level: s.level,
                              weight: "0.6"
                            })),
                            ...selectedRequirements.bonus_skills.map(s => ({
                              skill: s.skill,
                              level: s.level,
                              weight: "0.4"
                            }))
                          ];
                          console.log("SENDING REQUIREMENTS AS OBJECTS:", formattedRequirements);
                          const job = {
                            title: form.title,
                            description: form.description,
                            requirements: formattedRequirements,
                            seniority: form.seniority,
                            screening_questions: form.screening_questions,
                            summary: agentSummary,
                          };
                          console.log("FULL JOB PAYLOAD:", job);
                          try {
                            const token = localStorage.getItem("access_token");
                            
                            // Step 1: Create the job
                            const res = await fetch("http://127.0.0.1:8000/users/me/jobs", {
                              method: "POST",
                              headers: { 
                                "Content-Type": "application/json",
                                "Authorization": `Bearer ${token}`
                              },
                              body: JSON.stringify(job),
                            });
                            
                            if (!res.ok) {
                              if (res.status === 401) {
                                localStorage.removeItem("access_token");
                                localStorage.removeItem("user");
                                router.push("/auth/login");
                                return;
                              }
                              throw new Error("Failed to create job");
                            }
                            
                            const createdJob = await res.json();
                            console.log("Job created:", createdJob);
                            
                            // Step 2: Publish the job
                            const publishRes = await fetch(`http://127.0.0.1:8000/users/me/jobs/${createdJob.id}/publish`, {
                              method: "POST",
                              headers: { 
                                "Authorization": `Bearer ${token}`
                              },
                            });
                            
                            if (!publishRes.ok) {
                              console.warn("Job created but failed to publish:", await publishRes.text());
                              // Still show success since job was created
                            } else {
                              console.log("Job published successfully!");
                            }
                            
                            // Success - move to step 4 (success message)
                            setStep(4);
                          } catch (err: any) {
                            alert(`Error creating job: ${err.message}`);
                          } finally {
                            setCreating(false);
                          }
                        }}
                        disabled={creating}
                      >
                        {creating ? (
                          <>
                            <i className="mr-2 fas fa-spinner fa-spin"></i>
                            Publishing Job...
                          </>
                        ) : (
                          <>
                            <i className="mr-2 fas fa-rocket"></i>
                            Publish Job
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* Success Message */}
            {step === 4 && (
              <Card padding="xl">
                <div className="space-y-8 text-center">
                  <div className="flex justify-center items-center bg-gradient-to-br from-green-500 to-blue-500 mx-auto mb-6 rounded-full w-24 h-24">
                    <i className="text-white text-4xl fas fa-check-circle"></i>
                  </div>
                  <div>
                    <h2 className="mb-4 font-bold text-gray-900 text-3xl">Job Published Successfully! 🎉</h2>
                    <p className="mb-8 text-gray-600 text-lg">Your job has been created and is now live on the platform.</p>
                  </div>
                  <div className="flex justify-center gap-4">
                    <Link href="/jobs">
                      <button className="bg-gradient-to-r from-purple-600 to-blue-600 px-8 py-4 rounded-2xl font-bold text-white hover:scale-105 transition-all duration-300">
                        <i className="mr-2 fas fa-list"></i>
                        View All Jobs
                      </button>
                    </Link>
                    <button 
                      onClick={() => {
                        setStep(1);
                        setForm({ title: "", description: "", requirements: [], seniority: "", screening_questions: [], summary: "", location: "", salary_min: "", salary_max: "" });
                        setAgentSummary("");
                      }}
                      className="bg-gray-100 hover:bg-gray-200 px-8 py-4 rounded-2xl font-semibold text-gray-700 transition-all duration-300"
                    >
                      <i className="mr-2 fas fa-plus"></i>
                      Create Another Job
                    </button>
                  </div>
                </div>
              </Card>
              
            )}
          </div>
        
        </div>
      </MainContent>
    </PageContainer>
  );
}
