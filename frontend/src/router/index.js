import Vue from 'vue'
import Router from 'vue-router'
import Index from '@/views/Index'
import Labeler from '@/views/Labeler'
import Help from '@/views/Help'
import License from '@/views/License'

Vue.use(Router)

export default new Router({
	routes: [
		{
			path: '/',
			name: 'home',
			component: Index,
			props: true
		},
		{
			path: '/labeler',
			name: 'labeler',
			component: Labeler,
			props: true
		},
		{
			path: '/help',
			name: 'help',
			component: Help
		},
		{
			path: '/license',
			name: 'license',
			component: License
		}
	]
})