import Link from "next/link";

interface HeaderProps {
  title: string;
  subtitle?: string;
  backHref?: string;
  backLabel?: string;
  user?: {
    full_name?: string;
    username: string;
  } | null;
  onLogout?: () => void;
  actions?: React.ReactNode;
}

export function AppHeader({ 
  title, 
  subtitle, 
  backHref, 
  backLabel = "Back", 
  user, 
  onLogout,
  actions 
}: HeaderProps) {
  return (
    <header className="top-0 z-50 sticky bg-white/90 shadow-xl backdrop-blur-md border-gray-200/50 border-b">
      <div className="mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            {backHref && (
              <Link
                href={backHref}
                className="flex items-center bg-gradient-to-r from-purple-600 hover:from-purple-700 to-blue-600 hover:to-blue-700 shadow-lg hover:shadow-xl mr-4 px-4 py-2 rounded-xl font-semibold text-white hover:scale-105 transition-all duration-300 transform"
              >
                <i className="fa-arrow-left mr-2 fas"></i>
                {backLabel}
              </Link>
            )}
            <div className="flex items-center">
              <div className="flex justify-center items-center bg-gradient-to-r from-purple-600 to-blue-600 shadow-lg mr-3 rounded-xl w-10 h-10">
                <span className="font-bold text-white text-sm">CV2</span>
              </div>
              <div>
                <h1 className="font-bold text-gray-900 text-xl">{title}</h1>
                {subtitle && <p className="text-gray-600 text-sm">{subtitle}</p>}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {actions}
            {user && (
              <>
                <div className="flex items-center space-x-3">
                  <div className="flex justify-center items-center bg-gradient-to-r from-green-100 to-blue-100 rounded-full w-8 h-8">
                    <i className="text-purple-600 text-sm fas fa-user"></i>
                  </div>
                  <span className="hidden md:block font-medium text-gray-700">
                    {user.full_name || user.username}
                  </span>
                </div>
                {onLogout && (
                  <button
                    onClick={onLogout}
                    className="bg-gray-100 hover:bg-gray-200 hover:shadow-md px-4 py-2 rounded-xl font-medium text-gray-700 transition-all duration-300"
                  >
                    <i className="mr-2 fas fa-sign-out-alt"></i>
                    <span className="hidden sm:inline">Logout</span>
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function PageContainer({ children, className = "" }: PageContainerProps) {
  return (
    <div className={`bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 min-h-screen ${className}`}>
      {children}
    </div>
  );
}

interface MainContentProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "4xl" | "6xl" | "7xl";
}

export function MainContent({ children, className = "", maxWidth = "7xl" }: MainContentProps) {
  const maxWidthClass = {
    sm: "max-w-sm",
    md: "max-w-md", 
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
    "4xl": "max-w-4xl",
    "6xl": "max-w-6xl",
    "7xl": "max-w-7xl"
  }[maxWidth];

  return (
    <main className={`mx-auto px-4 sm:px-6 lg:px-8 py-8 ${maxWidthClass} ${className}`}>
      {children}
    </main>
  );
}

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: "sm" | "md" | "lg" | "xl";
}

export function Card({ children, className = "", hover = false, padding = "lg" }: CardProps) {
  const paddingClass = {
    sm: "p-4",
    md: "p-6", 
    lg: "p-8",
    xl: "p-10"
  }[padding];

  const hoverClass = hover 
    ? "hover:shadow-2xl hover:scale-[1.02] transform transition-all duration-500" 
    : "transition-all duration-300";

  return (
    <div className={`bg-white/90 shadow-xl backdrop-blur-md border border-white/20 rounded-3xl ${paddingClass} ${hoverClass} ${className}`}>
      {children}
    </div>
  );
}

interface ButtonProps {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "danger" | "success" | "outline";
  size?: "sm" | "md" | "lg";
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit";
  href?: string;
}

export function Button({ 
  children, 
  variant = "primary", 
  size = "md", 
  className = "", 
  onClick,
  disabled = false,
  type = "button",
  href
}: ButtonProps) {
  const baseClass = "inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const variantClass = {
    primary: "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg hover:shadow-xl focus:ring-purple-500",
    secondary: "bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 hover:border-purple-300 shadow-lg hover:shadow-xl focus:ring-gray-500",
    danger: "bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white shadow-lg hover:shadow-xl focus:ring-red-500",
    success: "bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white shadow-lg hover:shadow-xl focus:ring-green-500",
    outline: "bg-transparent border-2 border-purple-600 text-purple-600 hover:bg-purple-600 hover:text-white focus:ring-purple-500"
  }[variant];

  const sizeClass = {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-2.5 text-sm",
    lg: "px-6 py-3 text-base"
  }[size];

  const disabledClass = disabled ? "opacity-50 cursor-not-allowed transform-none hover:scale-100" : "";

  const classes = `${baseClass} ${variantClass} ${sizeClass} ${disabledClass} ${className}`;

  if (href) {
    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={classes}
    >
      {children}
    </button>
  );
}

interface SectionHeaderProps {
  icon: string;
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export function SectionHeader({ icon, title, subtitle, actions }: SectionHeaderProps) {
  return (
    <div className="flex justify-between items-start mb-6">
      <div>
        <h2 className="flex items-center mb-2 font-bold text-gray-900 text-2xl">
          <i className={`mr-3 text-purple-600 ${icon}`}></i>
          {title}
        </h2>
        {subtitle && <p className="text-gray-600">{subtitle}</p>}
      </div>
      {actions && <div>{actions}</div>}
    </div>
  );
}

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg" | "xl";
  message?: string;
}

export function LoadingSpinner({ size = "lg", message }: LoadingSpinnerProps) {
  const sizeClass = {
    sm: "w-8 h-8",
    md: "w-16 h-16", 
    lg: "w-24 h-24",
    xl: "w-32 h-32"
  }[size];

  return (
    <PageContainer>
      <div className="flex flex-col justify-center items-center min-h-screen">
        <div className={`border-purple-600 border-b-4 rounded-full ${sizeClass} animate-spin`}></div>
        {message && (
          <p className="mt-4 font-medium text-gray-600 text-lg">{message}</p>
        )}
      </div>
    </PageContainer>
  );
}

interface ErrorDisplayProps {
  title?: string;
  message: string;
  icon?: string;
  actions?: React.ReactNode;
}

export function ErrorDisplay({ 
  title = "Error", 
  message, 
  icon = "fas fa-exclamation-triangle",
  actions 
}: ErrorDisplayProps) {
  return (
    <PageContainer>
      <div className="flex flex-col justify-center items-center min-h-screen">
        <Card className="max-w-md text-center">
          <div className="flex justify-center items-center bg-red-100 mx-auto mb-4 rounded-full w-16 h-16">
            <i className={`text-red-600 text-2xl ${icon}`}></i>
          </div>
          <h2 className="mb-2 font-bold text-gray-900 text-xl">{title}</h2>
          <p className="mb-6 text-gray-600">{message}</p>
          {actions}
        </Card>
      </div>
    </PageContainer>
  );
}
