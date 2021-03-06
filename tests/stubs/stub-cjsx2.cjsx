# Renders an activity feed toggle in navigation

NavActions = require 'actions/nav-actions'
AppConstants = require 'constants/app-constants'
moment = require 'moment-timezone'

LocalSettingsActions = require 'actions/local-settings-actions'
LocalSettingsStore = require 'stores/local-settings-store'

transitionToCurrentRoute = require 'utils/transition-to-current-route'

NavActivityFeedToggle = React.createClass

  contextTypes:
    location: React.PropTypes.object
    history: React.PropTypes.object
    params: React.PropTypes.object
    router: React.PropTypes.object
    routes: React.PropTypes.array

  propTypes:
    isOpen: React.PropTypes.bool
    lastOpenedAt: React.PropTypes.number
    lastClosedAt: React.PropTypes.number
    hasNewNotifications: React.PropTypes.bool
    showPipe: React.PropTypes.bool

module.exports = NavActivityFeedToggle