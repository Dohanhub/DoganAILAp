import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

interface LoginForm {
  username: string
  password: string
}

export default function Login() {
  const navigate = useNavigate()
  const { login, isLoading } = useAuthStore()
  const [isRegistering, setIsRegistering] = useState(false)
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>()

  const onSubmit = async (data: LoginForm) => {
    try {
      await login(data.username, data.password)
      navigate('/dashboard')
    } catch (error) {
      console.error('Login error:', error)
      toast.error('Login failed - please try again')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      {/* Premium Background Pattern */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-slate-900 opacity-50"></div>
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/20 via-transparent to-blue-900/20"></div>
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(circle at 25% 25%, rgba(16, 185, 129, 0.1) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(59, 130, 246, 0.1) 0%, transparent 50%)'
        }}></div>
      </div>
      
      {/* Floating Elements */}
      <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-green-400/10 to-emerald-600/10 rounded-full blur-2xl"></div>
      <div className="absolute bottom-20 right-20 w-40 h-40 bg-gradient-to-br from-blue-400/10 to-indigo-600/10 rounded-full blur-2xl"></div>
      <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-gradient-to-br from-purple-400/10 to-pink-600/10 rounded-full blur-xl"></div>
      
      <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl w-full">
          {/* World-Class Enterprise Platform Card */}
          <div className="bg-white/5 backdrop-blur-3xl shadow-2xl rounded-3xl overflow-hidden border border-white/10 relative">
            {/* Premium Glass Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-white/5"></div>
            
            <div className="flex relative z-10">
              {/* Left Panel - Enterprise Login */}
              <div className="flex-1 px-8 sm:px-12 lg:px-16 py-16">
                <div className="max-w-md mx-auto">
                  {/* National Platform Header */}
                  <div className="text-center mb-12">
                    {/* Elite Logo */}
                    <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-green-500 to-emerald-600 rounded-3xl mb-8 shadow-2xl border border-white/20">
                      <div className="w-14 h-14">
                        <svg viewBox="0 0 64 64" fill="none" className="w-full h-full">
                          <path d="M32 8L12 24L32 40L52 24L32 8Z" fill="white" fillOpacity="0.95"/>
                          <path d="M32 28L12 44L32 60L52 44L32 28Z" fill="white" fillOpacity="0.75"/>
                          <circle cx="32" cy="28" r="4" fill="white"/>
                          <path d="M20 16L44 16L44 20L20 20Z" fill="white" fillOpacity="0.6"/>
                          <path d="M20 36L44 36L44 40L20 40Z" fill="white" fillOpacity="0.4"/>
                        </svg>
                      </div>
                    </div>
                    
                    {/* Platform Title */}
                    <h1 className="text-3xl font-bold text-white mb-3">
                      Kingdom of Saudi Arabia
                    </h1>
                    <p className="text-xl text-emerald-300 font-semibold mb-2">
                      National Compliance Platform
                    </p>
                    <p className="text-sm text-slate-300 font-medium">
                      ScenarioKit • AI-Powered Regulatory Excellence
                    </p>
                  </div>

                  {/* Enterprise Authentication Card */}
                  <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20 shadow-xl">
                    {/* Access Header */}
                    <div className="text-center mb-8">
                      <h2 className="text-2xl font-bold text-white mb-2">
                        Secure Access Portal
                      </h2>
                      <p className="text-slate-300">
                        Authorized Personnel Only
                      </p>
                    </div>

                    <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
                      {/* Username Field */}
                      <div>
                        <label htmlFor="username" className="block text-sm font-semibold text-slate-200 mb-3">
                          Username / Employee ID
                        </label>
                        <div className="relative">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <svg className="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                          </div>
                          <input
                            {...register('username', { required: 'Username is required' })}
                            type="text"
                            autoComplete="username"
                            className="block w-full pl-12 pr-4 py-4 text-white bg-white/10 backdrop-blur-sm border border-white/30 rounded-xl placeholder-slate-400 shadow-lg focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30 transition-all duration-300"
                            placeholder="Enter your credentials"
                          />
                          {errors.username && (
                            <p className="mt-2 text-sm text-red-400 flex items-center">
                              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                              </svg>
                              {errors.username.message}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Password Field */}
                      <div>
                        <label htmlFor="password" className="block text-sm font-semibold text-slate-200 mb-3">
                          Secure Password
                        </label>
                        <div className="relative">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <svg className="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                          </div>
                          <input
                            {...register('password', { required: 'Password is required' })}
                            type="password"
                            autoComplete="current-password"
                            className="block w-full pl-12 pr-4 py-4 text-white bg-white/10 backdrop-blur-sm border border-white/30 rounded-xl placeholder-slate-400 shadow-lg focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30 transition-all duration-300"
                            placeholder="Enter secure password"
                          />
                          {errors.password && (
                            <p className="mt-2 text-sm text-red-400 flex items-center">
                              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                              </svg>
                              {errors.password.message}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Security Options */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <input
                            id="remember-me"
                            name="remember-me"
                            type="checkbox"
                            className="h-4 w-4 rounded border-white/30 text-emerald-500 bg-white/10 focus:ring-emerald-400 focus:ring-2"
                          />
                          <label htmlFor="remember-me" className="ml-3 block text-sm font-medium text-slate-300">
                            Secure session
                          </label>
                        </div>

                        <div className="text-sm">
                          <a href="#" className="font-semibold text-emerald-400 hover:text-emerald-300 transition-colors">
                            Access Recovery?
                          </a>
                        </div>
                      </div>

                      {/* Premium Login Button */}
                      <div>
                        <button
                          type="submit"
                          disabled={isLoading}
                          className="group relative w-full flex justify-center py-4 px-6 border border-transparent text-base font-bold rounded-xl text-white bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
                        >
                          {isLoading ? (
                            <>
                              <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Authenticating...
                            </>
                          ) : (
                            <>
                              <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                                <svg className="h-6 w-6 text-emerald-300 group-hover:text-emerald-200" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                                </svg>
                              </span>
                              ACCESS PLATFORM
                            </>
                          )}
                        </button>
                      </div>

                      {/* Alternative Access Methods */}
                      <div className="mt-8">
                        <div className="relative">
                          <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-white/20" />
                          </div>
                          <div className="relative flex justify-center text-sm">
                            <span className="bg-slate-800/50 backdrop-blur px-4 text-slate-300 font-medium">Alternative Access</span>
                          </div>
                        </div>

                        <div className="mt-6 grid grid-cols-2 gap-4">
                          <button
                            type="button"
                            className="flex w-full items-center justify-center rounded-xl border border-white/30 bg-white/5 backdrop-blur py-3 px-4 text-sm font-semibold text-white shadow-lg hover:bg-white/10 hover:border-white/40 transition-all duration-200"
                          >
                            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
                            </svg>
                            Government SSO
                          </button>
                          <button
                            type="button"
                            onClick={() => setIsRegistering(!isRegistering)}
                            className="flex w-full items-center justify-center rounded-xl border border-white/30 bg-white/5 backdrop-blur py-3 px-4 text-sm font-semibold text-white shadow-lg hover:bg-white/10 hover:border-white/40 transition-all duration-200"
                          >
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                            </svg>
                            Request Access
                          </button>
                        </div>
                      </div>
                    </form>

                    {/* Demo Credentials for Development */}
                    <div className="mt-8 p-4 bg-blue-500/10 border border-blue-400/20 rounded-xl backdrop-blur">
                      <div className="text-center">
                        <p className="text-sm font-semibold text-blue-300 mb-3">Development Access</p>
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          <div>
                            <span className="text-blue-300">Username:</span>
                            <code className="block bg-blue-500/20 text-blue-200 px-2 py-1 rounded mt-1 font-mono">admin</code>
                          </div>
                          <div>
                            <span className="text-blue-300">Password:</span>
                            <code className="block bg-blue-500/20 text-blue-200 px-2 py-1 rounded mt-1 font-mono">SecureP@ss2024!</code>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Panel - National Branding */}
              <div className="hidden lg:flex lg:flex-1 relative">
                <div className="w-full bg-gradient-to-br from-emerald-600 via-green-600 to-teal-700 relative overflow-hidden">
                  {/* Premium Pattern Overlay */}
                  <div className="absolute inset-0" style={{
                    backgroundImage: `radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%), radial-gradient(circle at 40% 80%, rgba(255,255,255,0.1) 0%, transparent 50%)`
                  }}></div>
                  
                  {/* Saudi Arabia National Elements */}
                  <div className="relative h-full flex flex-col justify-center px-12 py-16 text-white">
                    {/* National Header */}
                    <div className="text-center mb-12">
                      {/* Crown Symbol */}
                      <div className="inline-flex items-center justify-center w-32 h-32 bg-white/10 backdrop-blur rounded-full mb-8 border-2 border-white/30">
                        <svg viewBox="0 0 80 80" fill="none" className="w-20 h-20">
                          <path d="M40 10L20 30L40 50L60 30L40 10Z" fill="white" fillOpacity="0.9"/>
                          <path d="M40 35L20 55L40 75L60 55L40 35Z" fill="white" fillOpacity="0.7"/>
                          <circle cx="40" cy="35" r="6" fill="white"/>
                          <rect x="25" y="15" width="30" height="4" fill="white" fillOpacity="0.8"/>
                          <rect x="25" y="60" width="30" height="4" fill="white" fillOpacity="0.6"/>
                          <path d="M15 25L25 15L25 35L15 25Z" fill="white" fillOpacity="0.5"/>
                          <path d="M65 25L55 15L55 35L65 25Z" fill="white" fillOpacity="0.5"/>
                        </svg>
                      </div>
                      
                      <h1 className="text-5xl font-bold mb-4 leading-tight">
                        المملكة العربية السعودية
                      </h1>
                      <h2 className="text-4xl font-bold mb-6">
                        Kingdom of Saudi Arabia
                      </h2>
                      <p className="text-xl text-emerald-100 font-semibold mb-2">
                        National Regulatory Compliance Platform
                      </p>
                      <p className="text-lg text-emerald-200">
                        Vision 2030 • Digital Transformation Initiative
                      </p>
                    </div>

                    {/* Compliance Framework Stats */}
                    <div className="grid grid-cols-2 gap-6 mb-12">
                      <div className="bg-white/15 backdrop-blur-lg rounded-3xl p-6 border border-white/20 text-center transform hover:scale-105 transition-transform duration-300">
                        <div className="text-4xl font-bold text-white mb-2">114</div>
                        <div className="text-emerald-100 font-semibold text-sm">NCA Controls</div>
                        <div className="text-xs text-emerald-200 mt-1">Cybersecurity</div>
                      </div>
                      <div className="bg-white/15 backdrop-blur-lg rounded-3xl p-6 border border-white/20 text-center transform hover:scale-105 transition-transform duration-300">
                        <div className="text-4xl font-bold text-white mb-2">97</div>
                        <div className="text-emerald-100 font-semibold text-sm">SAMA Framework</div>
                        <div className="text-xs text-emerald-200 mt-1">Financial Services</div>
                      </div>
                      <div className="bg-white/15 backdrop-blur-lg rounded-3xl p-6 border border-white/20 text-center transform hover:scale-105 transition-transform duration-300">
                        <div className="text-4xl font-bold text-white mb-2">73</div>
                        <div className="text-emerald-100 font-semibold text-sm">PDPL Controls</div>
                        <div className="text-xs text-emerald-200 mt-1">Data Protection</div>
                      </div>
                      <div className="bg-white/15 backdrop-blur-lg rounded-3xl p-6 border border-white/20 text-center transform hover:scale-105 transition-transform duration-300">
                        <div className="text-4xl font-bold text-white mb-2">24/7</div>
                        <div className="text-emerald-100 font-semibold text-sm">AI Monitoring</div>
                        <div className="text-xs text-emerald-200 mt-1">Real-time</div>
                      </div>
                    </div>

                    {/* National Certifications */}
                    <div className="text-center">
                      <div className="inline-flex flex-wrap justify-center gap-3 text-sm mb-8">
                        <div className="flex items-center bg-white/10 backdrop-blur px-4 py-3 rounded-full border border-white/20">
                          <div className="w-3 h-3 bg-emerald-300 rounded-full mr-2 animate-pulse"></div>
                          <span className="text-white font-semibold">NCA Certified</span>
                        </div>
                        <div className="flex items-center bg-white/10 backdrop-blur px-4 py-3 rounded-full border border-white/20">
                          <div className="w-3 h-3 bg-emerald-300 rounded-full mr-2 animate-pulse"></div>
                          <span className="text-white font-semibold">SAMA Compliant</span>
                        </div>
                        <div className="flex items-center bg-white/10 backdrop-blur px-4 py-3 rounded-full border border-white/20">
                          <div className="w-3 h-3 bg-emerald-300 rounded-full mr-2 animate-pulse"></div>
                          <span className="text-white font-semibold">PDPL Ready</span>
                        </div>
                      </div>
                      
                      <div className="border-t border-white/20 pt-6">
                        <p className="text-emerald-200 text-sm font-medium">
                          Powering Digital Government • Securing National Infrastructure
                        </p>
                        <p className="text-emerald-300 text-xs mt-2">
                          Built for Saudi Arabia's Digital Future
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}