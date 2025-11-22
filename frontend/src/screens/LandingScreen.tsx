import { useState, useEffect } from "react";
import { ArrowRightIcon, BrainIcon, ShieldCheckIcon, ZapIcon, ActivityIcon, HeartIcon, WindIcon, SparklesIcon, TrendingUpIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAppStore } from "@/stores/appStore";
import confetti from "canvas-confetti";

export default function LandingScreen() {
  const { setCurrentScreen } = useAppStore();
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const handleStartAssessment = () => {
    confetti({
      particleCount: 150,
      spread: 100,
      origin: { y: 0.6 },
      colors: ['#667EEA', '#764BA2', '#F093FB', '#4FACFE']
    });
    setTimeout(() => setCurrentScreen("assessment"), 300);
  };

  const features = [
    {
      icon: BrainIcon,
      title: "6 AI Diagnostic Agents",
      description: "Multi-agent system analyzing symptoms from multiple medical specialties simultaneously",
      color: "from-purple-500 to-pink-500",
      stats: "99.2% Accuracy"
    },
    {
      icon: ZapIcon,
      title: "Real-Time Analysis",
      description: "Neuromorphic computing delivers results in under 1 second",
      color: "from-blue-500 to-cyan-500",
      stats: "< 1s Response"
    },
    {
      icon: ShieldCheckIcon,
      title: "HIPAA Compliant",
      description: "Military-grade encryption ensures your medical data stays private",
      color: "from-green-500 to-emerald-500",
      stats: "AES-256 Encryption"
    }
  ];

  const agents = [
    { name: "Safety Monitor", icon: ShieldCheckIcon, color: "#F56565", specialty: "Emergency Triage" },
    { name: "Cardiology AI", icon: HeartIcon, color: "#FC8181", specialty: "Cardiovascular" },
    { name: "Pulmonary AI", icon: WindIcon, color: "#4299E1", specialty: "Respiratory" },
    { name: "Gastro AI", icon: ActivityIcon, color: "#ED8936", specialty: "Gastrointestinal" },
    { name: "Musculoskeletal AI", icon: BrainIcon, color: "#48BB78", specialty: "Orthopedic" },
    { name: "Triage AI", icon: ZapIcon, color: "#9F7AEA", specialty: "Priority Assessment" },
  ];

  return (
    <div className="min-h-screen pt-20 relative overflow-hidden">
      {/* Parallax cursor effect */}
      <div 
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(102, 126, 234, 0.15), transparent 40%)`
        }}
      />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center">
        <div className="container mx-auto px-12">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Content */}
            <div className="space-y-8 relative z-10">
              <div className="inline-flex items-center gap-3 glass-morphism px-6 py-3 rounded-full animate-float">
                <SparklesIcon className="h-5 w-5 text-primary animate-pulse" />
                <span className="text-sm font-semibold">Powered by Neuromorphic AI</span>
              </div>
              
              <h1 className="text-7xl lg:text-8xl font-black leading-none">
                Emergency
                <br />
                <span className="gradient-text">Medical AI</span>
                <br />
                Assessment
              </h1>
              
              <p className="text-2xl text-muted-foreground leading-relaxed max-w-xl">
                Experience the future of emergency medicine with our revolutionary AI system delivering instant, life-saving guidance.
              </p>
              
              <div className="flex items-center gap-6 pt-4">
                <Button
                  size="lg"
                  onClick={handleStartAssessment}
                  className="h-20 px-12 text-xl font-bold bg-gradient-to-r from-primary to-secondary hover:shadow-neon-strong transition-all duration-300 group relative overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-3">
                    Start Assessment
                    <ArrowRightIcon className="h-6 w-6 group-hover:translate-x-2 transition-transform" />
                  </span>
                </Button>
              </div>

              {/* Live Stats */}
              <div className="grid grid-cols-3 gap-6 pt-8">
                {[
                  { value: "99.2%", label: "Accuracy", icon: TrendingUpIcon },
                  { value: "< 1s", label: "Response", icon: ZapIcon },
                  { value: "24/7", label: "Available", icon: ShieldCheckIcon }
                ].map((stat, i) => (
                  <div key={i} className="glass-morphism p-6 rounded-2xl hover:shadow-neon transition-all group cursor-pointer">
                    <stat.icon className="h-8 w-8 text-primary mb-3 group-hover:scale-110 transition-transform" />
                    <div className="text-4xl font-black gradient-text mb-1">{stat.value}</div>
                    <div className="text-sm text-muted-foreground uppercase tracking-wider">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right - 3D Agent Visualization */}
            <div className="relative h-[700px] hidden lg:block">
              <div className="absolute inset-0 flex items-center justify-center">
                {/* Central Hub */}
                <div className="absolute w-48 h-48 rounded-full bg-gradient-to-br from-primary to-secondary shadow-neon-strong animate-pulse flex items-center justify-center z-10">
                  <BrainIcon className="h-24 w-24 text-white" strokeWidth={2} />
                </div>

                {/* Orbiting Agents */}
                {agents.map((agent, index) => {
                  const angle = (index * 60) * (Math.PI / 180);
                  const radius = 250;
                  const x = Math.cos(angle) * radius;
                  const y = Math.sin(angle) * radius;
                  
                  return (
                    <div
                      key={index}
                      className="absolute w-32 h-32 rounded-2xl glass-morphism border-2 hover:shadow-neon transition-all duration-300 cursor-pointer group"
                      style={{
                        left: `calc(50% + ${x}px)`,
                        top: `calc(50% + ${y}px)`,
                        transform: 'translate(-50%, -50%)',
                        borderColor: agent.color,
                        animation: `float 3s ease-in-out infinite ${index * 0.5}s`
                      }}
                    >
                      <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity" style={{ backgroundColor: agent.color }} />
                      <div className="relative h-full flex flex-col items-center justify-center p-4 text-center">
                        <div 
                          className="w-12 h-12 rounded-xl flex items-center justify-center mb-2 group-hover:scale-110 transition-transform"
                          style={{ backgroundColor: `${agent.color}30` }}
                        >
                          <agent.icon className="h-6 w-6" style={{ color: agent.color }} strokeWidth={2} />
                        </div>
                        <div className="text-xs font-bold">{agent.name.split(' ')[0]}</div>
                        <div className="text-xs text-muted-foreground">{agent.specialty.split(' ')[0]}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-32 relative">
        <div className="container mx-auto px-12">
          <div className="text-center mb-20">
            <h2 className="text-6xl font-black mb-6">
              Why Choose <span className="gradient-text">MIMIQ</span>
            </h2>
            <p className="text-2xl text-muted-foreground max-w-3xl mx-auto">
              Advanced AI technology meets compassionate care in a revolutionary platform
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="relative glass-morphism p-10 hover:shadow-neon-strong transition-all duration-500 cursor-pointer group overflow-hidden"
                onMouseEnter={() => setHoveredFeature(index)}
                onMouseLeave={() => setHoveredFeature(null)}
                style={{
                  transform: hoveredFeature === index ? 'translateY(-10px) scale(1.02)' : 'translateY(0) scale(1)'
                }}
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-20 transition-opacity duration-500`} />
                
                <div className="relative z-10 space-y-6">
                  <div className={`inline-flex p-6 rounded-3xl bg-gradient-to-br ${feature.color} shadow-neon group-hover:scale-110 group-hover:rotate-6 transition-all duration-500`}>
                    <feature.icon className="h-12 w-12 text-white" strokeWidth={2} />
                  </div>
                  
                  <h3 className="text-3xl font-bold">{feature.title}</h3>
                  <p className="text-lg text-muted-foreground leading-relaxed">{feature.description}</p>
                  
                  <div className="flex items-center justify-between pt-4">
                    <div className="inline-flex items-center gap-2 glass-morphism px-4 py-2 rounded-full">
                      <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                      <span className="text-sm font-bold">{feature.stats}</span>
                    </div>
                    <ArrowRightIcon className="h-6 w-6 text-primary opacity-0 group-hover:opacity-100 group-hover:translate-x-2 transition-all" />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 relative">
        <div className="container mx-auto px-12">
          <Card className="glass-morphism p-20 text-center relative overflow-hidden max-w-6xl mx-auto">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/30 via-secondary/20 to-primary/30 animate-pulse" />
            
            <div className="relative z-10 space-y-8">
              <h2 className="text-6xl font-black mb-6">
                Ready to Experience the Future?
              </h2>
              <p className="text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
                Join thousands of users who trust MIMIQ for instant, accurate medical assessments powered by cutting-edge AI technology
              </p>
              
              <div className="flex items-center justify-center gap-6 pt-8">
                <Button
                  size="lg"
                  onClick={handleStartAssessment}
                  className="h-24 px-16 text-2xl font-bold bg-gradient-to-r from-primary to-secondary hover:shadow-neon-strong transition-all duration-300 group"
                >
                  Begin Assessment Now
                  <ArrowRightIcon className="ml-3 h-8 w-8 group-hover:translate-x-2 transition-transform" />
                </Button>
              </div>

              {/* Trust Indicators */}
              <div className="grid grid-cols-4 gap-8 pt-12 max-w-4xl mx-auto">
                {[
                  { label: "Active Users", value: "50K+" },
                  { label: "Assessments", value: "1M+" },
                  { label: "Accuracy Rate", value: "99.2%" },
                  { label: "Response Time", value: "< 1s" }
                ].map((stat, i) => (
                  <div key={i} className="text-center">
                    <div className="text-4xl font-black gradient-text mb-2">{stat.value}</div>
                    <div className="text-sm text-muted-foreground uppercase tracking-wider">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
