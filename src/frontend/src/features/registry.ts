// Modular feature registry for plug-and-play UI
import Dashboard from './dashboard'
import Organizations from './organizations'
import Assessments from './assessments'
import Risks from './risks'
import Frameworks from './frameworks'
import Reports from './reports'
import Settings from './settings'
import {
  HomeIcon,
  BuildingOfficeIcon,
  ClipboardDocumentCheckIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline'

export const features = [
  {
    name: 'Dashboard',
    path: '/dashboard',
    icon: HomeIcon,
    component: Dashboard,
  },
  {
    name: 'Organizations',
    path: '/organizations',
    icon: BuildingOfficeIcon,
    component: Organizations,
  },
  {
    name: 'Assessments',
    path: '/assessments',
    icon: ClipboardDocumentCheckIcon,
    component: Assessments,
  },
  {
    name: 'Risks',
    path: '/risks',
    icon: ExclamationTriangleIcon,
    component: Risks,
  },
  {
    name: 'Frameworks',
    path: '/frameworks',
    icon: DocumentTextIcon,
    component: Frameworks,
  },
  {
    name: 'Reports',
    path: '/reports',
    icon: ChartBarIcon,
    component: Reports,
  },
  {
    name: 'Settings',
    path: '/settings',
    icon: Cog6ToothIcon,
    component: Settings,
  },
]
