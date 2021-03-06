var JS_ROOT = "famille/static/js/",
    BUILD_ROOT = JS_ROOT + "build/";

module.exports = function(grunt) {
    grunt.initConfig({
        // connect: {
        //     test_server: {
        //         options: {
        //             port: 8001,
        //             base: "famille/static/js",
        //             keepalive: grunt.option('keepalive')
        //         }
        //     }
        // },
        // mocha_phantomjs: {
        //     all: {
        //         options: {
        //             urls: ['http://localhost:8001/mocha.html']
        //         }
        //     }
        // },
        //** Bundleing JS tasks **
        browserify: {
            options: {
                debug: true
            },
            search: {
                dest: BUILD_ROOT + "search.js",
                src: [JS_ROOT + "search/app.js"]
            },
            famille_account: {
                dest: BUILD_ROOT + "famille_account.js",
                src: [JS_ROOT + "account/famille.js"]
            },
            prestataire_account: {
                dest: BUILD_ROOT + "prestataire_account.js",
                src: [JS_ROOT + "account/prestataire.js"]
            },
            profile: {
                dest: BUILD_ROOT + "profile.js",
                src: [JS_ROOT + "profile/app.js"]
            },
            advanced: {
                dest: BUILD_ROOT + "advanced.js",
                src: [JS_ROOT + "account/advanced.js"]
            },
            premium: {
                dest: BUILD_ROOT + "premium.js",
                src: [JS_ROOT + "account/premium.js"]
            },
            messages: {
                dest: BUILD_ROOT + "messages.js",
                src: [JS_ROOT + "account/messages.js"]
            },
            contact_us: {
                dest: BUILD_ROOT + "contact_us.js",
                src: [JS_ROOT + "contact_us.js"]
            }
        },
        watch: {
            options: {
                atBegin: true
            },
            all: {
                files: [
                    JS_ROOT + "*.js",
                    JS_ROOT + 'search/**/*.js',
                    JS_ROOT + 'account/**/*.js',
                    JS_ROOT + 'profile/**/*.js'
                ],
                tasks: ['build']
            }
        }
    });

    // Load tasks from "grunt-sample" grunt plugin installed via Npm.
    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    // grunt.loadNpmTasks('grunt-contrib-connect');
    // grunt.loadNpmTasks('grunt-mocha-phantomjs');

    // App tasks
    grunt.registerTask('build', [
        'browserify:search',
        'browserify:famille_account',
        'browserify:prestataire_account',
        'browserify:profile',
        'browserify:advanced',
        'browserify:premium',
        'browserify:messages',
        'browserify:contact_us'
    ]);
};
