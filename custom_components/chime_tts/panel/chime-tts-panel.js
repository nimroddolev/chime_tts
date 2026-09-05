import { CHAPTER_ICONS } from "./chapter-icons.js";
import {
  EMPTY_CHIME_SET_SLOT_MACHINE_STYLES,
  renderEmptyChimeSetSlotMachine,
} from "/api/chime_tts/chime-set-slot-machine.js";

const PANEL_TAG = "chime-tts-settings-panel";
const AUDIO_FILE_ACCEPT = ".aac,.aif,.aiff,.ape,.flac,.m4a,.mp3,.ogg,.oga,.wav,.wma";
const AUDIO_FILE_EXTENSIONS = new Set(AUDIO_FILE_ACCEPT.split(","));
const PANEL_TRANSLATION_FALLBACKS = {"loading.settings":"Loading Chime TTS settings","loading.profiles":"Loading notification profiles...","loading.logs":"Loading Chime TTS log events...","loading.items":"Loading items...","chapter.settings":"Settings","chapter.configuration":"Configuration","chapter.configuration_description":"Set default providers, playback options, folder paths, and integration-wide behavior for Chime TTS.","chapter.profiles":"Profiles","chapter.session":"Session","chapter.project":"Project","section.notify_profiles_title":"Notification Profiles","section.notify_profiles_description":"Create custom chime services to easily send Chime TTS notifications in automations and scripts.","section.logs_title":"Logs","section.logs_description":"Review Chime TTS events captured during this Home Assistant session, including actions, generated media, and raw log output.","section.about_title":"Support & Info","section.about_description":"Find documentation, support, bug reporting, feature request, and project support links for Chime TTS.","action.reload":"Reload","action.reset":"Reset","action.reset_section":"Reset Section","action.save":"Save","action.restart":"Restart","action.restart_home_assistant":"Restart Home Assistant","action.cancel":"Cancel","action.discard":"Discard","action.close":"Close","action.open":"Open","action.browse":"Browse","action.use_anyway":"Use Anyway","action.expand":"Expand","action.collapse":"Collapse","action.expand_all":"Expand All","action.collapse_all":"Collapse All","action.show_advanced":"Show Advanced","action.hide_advanced":"Hide Advanced","action.add_profile":"+ Add Profile","action.raw_logs":"Raw Logs","action.copy_logs":"Copy Logs","action.copy_yaml":"Copy YAML","action.repeat":"Repeat","action.send":"Send","action.test":"Test","action.delete":"Delete","action.rename":"Rename","action.refresh":"Refresh","action.new_folder":"New Folder","action.upload":"Upload","action.upload_files":"Upload Files","action.upload_folder":"Upload Folder","action.create_folder":"Create Folder","action.overwrite_existing":"Overwrite Existing","action.upload_non_existing":"Upload {count} Non-Existing","action.select_folder":"Select folder","action.play_preview":"Play preview","action.pause_preview":"Pause preview","action.loading_preview":"Loading preview","aria.collapse_section":"Collapse section","aria.expand_section":"Expand section","aria.collapse_named":"Collapse {title}","aria.expand_named":"Expand {title}","aria.collapse_profile":"Collapse profile","aria.expand_profile":"Expand profile","aria.open_help":"Open help for {title}","aria.open_raw_logs":"Open the raw Home Assistant logs filtered to Chime TTS","aria.play_logo_animation":"Play Chime TTS logo animation","aria.logo":"Chime TTS logo","aria.collapse_log":"Collapse log row","aria.expand_log":"Expand log row","aria.close_test":"Close test input","aria.test_profile":"Test profile","aria.delete_profile":"Delete profile","aria.close_folder_browser":"Close folder browser","aria.more_actions":"More actions","aria.open_named":"Open {title}","aria.pause_named":"Pause {title}","aria.play_named":"Play {title}","aria.rename_named":"Rename {title}","aria.delete_named":"Delete {title}","aria.close_overwrite":"Close overwrite dialog","aria.confirm_restart":"Confirm Home Assistant restart","aria.unsaved_changes":"Unsaved changes","label.required":"Required","label.enabled":"Enabled","label.target_media_players":"Target media players","label.locations":"Locations","label.current_folder":"Current folder","label.version":"Version {version}","label.profile":"Profile {number}","label.log_event":"Log event","label.audio_file":"audio file","label.item":"item","label.this_item":"this item","label.selected_folder":"selected folder","label.new_name":"New name","label.folder_name":"Folder name","label.add_media_player":"Add media player","placeholder.service_name":"Service name","placeholder.tts_text":"Enter TTS text","placeholder.search_folder":"Search current folder","placeholder.new_folder_name":"New folder name","placeholder.auto":"Auto{unit}","description.target_media_players":"Select one or more media_player entities to play the notification.","description.add_media_player":"Choose a media_player entity to append","title.restart":"Restart Home Assistant?","title.save_changes":"Save your changes?","title.reset_changes":"Reset Changes","title.rename_item":"Rename item","title.delete_item":"Delete item","title.overwrite_files":"Overwrite Existing Files?","notice.restart_required_title":"Restart Required","notice.restart_required":"Any changes to the folder path or its contents will require a restart to take effect.","notice.restart_providers":"Home Assistant needs to restart before newly installed TTS providers appear in Chime TTS.","notice.restart_saved":"Your changes have been saved, but they will not take effect until Home Assistant restarts.","notice.unsaved_changes":"You have unsaved changes. Save them before leaving this page?","notice.discard_changes":"Discarding your unsaved edits?","notice.rename_item":"Choose a new name for {name}.","notice.delete_item":"Delete {name}? This action cannot be undone.","notice.upload_folder":"Upload {count} file(s) from \"{source}\" into folder \"{destination}\"?","notice.upload_conflicts_all":"Those files already exist in the folder \"{destination}\".","notice.upload_conflicts":"{count} file(s) already exist in the folder \"{destination}\".","status.changed":"Changed","status.copied":"Copied","status.sent":"Sent","status.restarting":"Restarting...","status.restart_requested":"Home Assistant restart requested.","empty.profiles":"No Chime TTS notify profiles are configured yet.","empty.logs":"No Chime TTS logs have been captured in this Home Assistant session yet.","empty.raw_logs":"No raw logs were captured for this event.","empty.media_players":"No media players selected yet.","empty.folder":"No files or folders match this location.","picker.audio_files_found":"{count} audio file(s) found","picker.no_audio_files":"No audio files were found in this folder.","log.integration_initiation":"Integration initiation","log.notification":"Notification","log.configuration_update":"Configuration update","log.action_call":"Action call","log.warning":"Warning","log.error":"Error","validation.required":"This field is required.","validation.invalid_number":"Enter a valid number.","validation.invalid_yaml":"Enter valid YAML.","validation.timeout":"The timeout value is invalid.","validation.timeout_sub":"Enter a valid timeout duration.","validation.tts_platform_none":"No TTS platforms were detected. Add at least one TTS integration first.","validation.tts_platform_select":"The selected TTS platform was not found.","validation.temp_path":"The temp folder must be inside a configured media directory.","validation.www_path":"The say_url output folder must be inside an external directory, /media, or /config/www.","error.load_panel":"Unable to load Chime TTS panel.","error.load_profiles":"Unable to load notification profiles.","error.validate_folder":"Unable to validate this folder path right now.","error.restart":"Unable to request a Home Assistant restart.","error.copy_logs":"Unable to copy logs to the clipboard.","error.copy_yaml":"Unable to copy YAML to the clipboard.","error.repeat":"Unable to repeat this action.","error.save":"Unable to save Chime TTS settings.","error.browse_folders":"Unable to browse folders.","error.play_chime_preview":"Unable to play this chime preview.","error.play_audio_preview":"Unable to play this audio preview.","error.browser_action":"Unable to complete that browser action.","error.upload_files":"Unable to upload the selected files.","error.folder_name_required":"Enter a folder name.","error.new_name_required":"Enter a new name.","error.folder_not_selectable":"That folder cannot be selected for this field.","error.send_notification":"Unable to send notify.{service}."};
const IS_DECEMBER = new Date().getMonth() === 11;
const SNOWFLAKE_SVG = `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M12 2v20M3.34 7l17.32 10M3.34 17L20.66 7M12 2l-2.2 2.2M12 2l2.2 2.2M12 22l-2.2-2.2M12 22l2.2-2.2M3.34 7l3 .8M3.34 7l.8 3M20.66 17l-3-.8M20.66 17l-.8-3M3.34 17l.8-3M3.34 17l3-.8M20.66 7l-.8 3M20.66 7l-3 .8" fill="none" stroke="currentColor" stroke-width="1.45" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const SANTA_HAT_SVG = `<svg xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.w3.org/2000/svg" xmlns:cc="http://web.resource.org/cc/" xmlns:dc="http://purl.org/dc/elements/1.1/" id="svg2" viewBox="0 0 410.44 285.17" version="1.0">
  <g id="layer1" transform="translate(-8.9025 -24.385)">
    <path id="path1309" d="m234.1 28.783c-28.1 7.734-56.9 23.115-77.16 38.007-20.27 14.892-73.194 52.42-85.278 64.31-11.716 11.53-25.555 15.55-31.611 29.75-2.335 5.48 15.837 22.01 19.398 23.72 9.241 4.46 24.304-3.44 31.178-3.91 22.303-1.53 45.163-4.5 67.763 10.79-4.18 4.22 2.45-0.32-6.09 36.7-3.01 13.05-9.6 46.92-1.51 53.38 8.04 6.42 12.95-18.61 20.94-14.78-0.01 0.01 0 0.02-0.01 0.03v0.02c0 0.01-0.01 0.03 0 0.03 0 0 0.02 0 0.02 0.01 0.02 0 0.08 0 0.13-0.01 0.01 0.01 0.03 0.01 0.05 0.01 0.06 0.03 0.11 0.06 0.16 0.09l0.05-0.13c3.78-0.97 33.26-13.96 60.18-8.74 15.17 2.94 39.37-5.31 53.29-9.62 22.07-6.82 53.07-12.99 72.73-13.35 14.48-0.26 27.58-8.46 41.52-9.41 8.22-0.56 0.59-27.07 0.42-29.87-0.81-13.45-17.56-34.13-26.19-52.5-8.62-18.37-23.08-41.7-39-59.986-15.92-18.29-37.4-41.972-52.53-49.259-15.12-7.287-17.95-13.675-48.45-5.282z" fill-rule="evenodd" stroke="#000" stroke-width=".83349px" fill="#d00000"/>
    <path id="path5882" opacity=".10112" d="m166.96 93.344c-18.24 4.416-33.85 62.696-56.32 72.826-14.701 6.62-54.752 16.69-51.191 18.4 9.241 4.46 24.304-3.44 31.178-3.91 22.303-1.53 45.163-4.5 67.763 10.79-4.18 4.22 2.45-0.32-6.09 36.7-3.01 13.05-9.6 46.92-1.51 53.38 8.04 6.42 12.95-18.61 20.94-14.78-0.01 0.01 0 0.02-0.01 0.03v0.02c0 0.01-0.01 0.03 0 0.03 0 0 0.02 0 0.02 0.01 0.02 0 0.08 0 0.13-0.01 0.01 0.01 0.03 0.01 0.05 0.01 0.06 0.03 0.11 0.06 0.16 0.09l0.05-0.13c3.78-0.97 33.26-13.96 60.18-8.74 15.17 2.94 39.37-5.31 53.29-9.62 22.07-6.82 53.07-12.99 72.73-13.35 14.48-0.26 27.58-8.46 41.52-9.41 8.22-0.56-51.09 4.52-27.45-12.58 10.48-7.58-104.99 15.81-149.32-34.77-43.89-50.09-37.45-89.509-56.12-84.986z" fill="#0e0000" fill-rule="evenodd"/>
    <path id="path5878" opacity=".26966" d="m41.923 154.63c3.551 2.36 27.398 32.52 30.215 30.41 0.341-3.33-2.44-4.64-4.397-5.02 2.62-3.33 3.114-6.82-1.432-7.11-5.04-0.89-10.543-1.52-5.133-6.94 2.498-3.04-0.168-8.44-1.701-11.18-4.03-2.18-7.066-6.11-8.718-8.79" fill-rule="evenodd" stroke="#000" stroke-width=".83016"/>
    <path id="path5003" opacity=".29404" d="m365.6 219.59c-7.45-2.65-16.8-5.7-23.39-5.29-4.53-3.82-8 0.89-11.92 2.14-0.66-7.36-11.51 3.11-16.29 3.17-3.4 1.95-1.06-5.8-7.14-2.85-7.55 0.71-12.23 1.23-17.83 3.66-1.35 8.01-13.45 12.53-15.27 3.74-6.59 2.88-18.86 8.45-18.94-0.64-10.57 8.2-10.9 15.6-21.22 19.56 0.92-7.1-22.37-10.91-25.54-3.47-6.39 2.57 1.33-9.32-7.91-6.05-10.4-3.02-4.34 17.93-25.55 9.37-11.81-0.38-5.27 16.71-13.06 23.88-2.08 7.53-11.08-2.63-14.73-2.06 0.85 11.92 3.41 7.88 0.72 15.99-1.61 10.17-3.75 15.26 7.43 17.38 3.62-4.91-0.18-2.83 0.63 6.21 6.46-1.88 14.94-12.64 14.07-1.58 4.39-6.67 18.26-10.15 18.08-17.34 7.03 0.74 14.91 8.58 20.83-0.95 5.95-7.04 14.51-10.31 14.6-4.87 7.23 6.76 7.95 5.39 15.48 3.67-1.94-8.71 17.59-0.6 7.28-9.27 4.1-4.11 15.19-6.5 21.59-5.08 5.67 8.26 22.95 8.94 25.64-1.74 0.56-8.41 13.68-11.28 18.58-5.47 8.53-7.48 21.99 3.39 29.33-2.35-6.6-8.56 9.32-14.16 12.3-7.59 5.84-3.14 11.27-14.42 17.66-6.34 7.35-2.4 16.33-5.73 22.55-8.22 4.66 7.69 16.74-0.23 11.51-9.54-2.84-6.65 9.31 3.28 6-5.16-3.76-9.08-9.04-21.69-15.51-21.28-8.82-2.2-14.04 3.75-14.41 12.16-0.11-6.14-10.52-0.15-15.98 2.08l-2.99 0.71-3.58-2.52" fill-rule="evenodd" stroke="#000" stroke-width=".60143px"/>
    <path id="path1307" d="m370.52 221.83c-7.45-2.64-14.35-3.01-20.94-2.61-4.53-3.82-9.9-2.56-13.82-1.31-0.65-7.36-9.61 6.57-14.39 6.63-3.4 1.95-1.06-5.8-7.13-2.86-7.56 0.72-16.32-3.97-21.93-1.54-1.35 8.01-13.45 12.53-15.26 3.74-6.6 2.88-14.78 13.65-14.86 4.57-12.39-0.54-17.69 11.63-28.01 15.59 0.92-7.1-15.58-6.95-18.75 0.5-6.39 2.57-1.7-13.44-10.93-10.17-10.4-3.03-10.12 17.69-22.53 13.48-11.81-0.38-10.16 11.36-17.95 18.52-2.08 7.53-6.19 2.74-9.84 3.3 6 8.52-18.39 6.74-11.15 19.87-1.6 10.17 0.85 17.47 12.03 19.59 3.62-4.9 7.09-8.92 7.9 0.13 6.46-1.88 14.95-12.64 14.08-1.58 4.38-6.68 18.25-10.15 18.08-17.34 7.02 0.74 14.9 8.58 20.82-0.95 5.96-7.05 6.94-1.3 7.03 4.14 7.23 6.75 15.53-3.63 23.05-5.35-1.94-8.71 17.6-0.59 7.28-9.27 4.1-4.1 15.19-6.5 21.6-5.07 5.62 5.33 22.94 8.93 25.63-1.75 0.56-8.4 13.68-11.28 18.59-5.47 8.52-7.48 21.98 3.39 29.32-2.34-6.6-8.57 9.32-14.16 12.3-7.6 5.84-3.13 11.28-14.42 17.67-6.34 7.35-2.39 16.32-5.72 22.54-8.22 4.66 7.69 16.75-0.22 11.51-9.53-2.84-6.65 9.31 3.27 6-5.17 0.08-9.65-3.56-24.6-15.51-21.27-8.81-2.2-14.04 3.74-14.41 12.16-0.11-6.14-14.02-3.92-19.48-1.7l-1.79 0.95-1.28 1.01" fill-rule="evenodd" stroke="#000" stroke-width=".60143px" fill="#fff"/>
    <path id="path3126" d="m155.68 210.89c3.14-40.85 23.79-59.45 20.15-92.12-2.15-19.313-19.54-4.68-13.87 13.44" stroke="#000" stroke-width=".83349px" fill="none"/>
    <path id="path3249" opacity=".11236" d="m163.98 266.62c-2.08 7.53-6.2 2.74-9.84 3.3 6 8.51-18.39 6.74-11.15 19.87-1.61 10.17 0.85 17.47 12.03 19.59 3.62-4.9 7.09-8.92 7.9 0.13 6.46-1.88 14.94-12.64 14.07-1.58 4.38-6.68 18.26-10.16 18.08-17.34 7.02 0.73 14.57 7.35 20.5-2.19 5.95-7.04 7.27-0.06 7.36 5.38 7.23 6.75 15.52-3.63 23.04-5.35-1.93-8.71 8.87-1.54 7.29-9.27-1.04-5.06 33.64-3.56 28.65-8.51-14.9-14.79-38.19 7.49-41.56 6.07-3.36-1.42-7.09-0.56-2.38-2.72s-6.74 1.39-16.28-1.99c-9.53-3.39-16.51 0.89-17.15 9.34-7.18-4.47-7.7 0.61-18.88 3.72 7.12-10.43-12.6-2.77-12.6-2.77s3.43-11.43-2.74-9.92c3.32-5.97-0.37-7.8-0.37-7.8s1.82-5.12-5.97 2.04z" fill-rule="evenodd"/>
    <path id="path2251" d="m46.945 146.24c-1.302-2.31-5.358-2.95-5.88-4.92 0.907-2.28-2.659-0.62-3.361-1.88-4.195 3.43-9.985 4.92-13.093 9.64 1.653-0.36 1.649-2.78-0.157-0.99-3.401 1.69-6.688 4.65-5.409 8.89 0.309 2.17-2.426 4.04 0.913 4.56-0.435 3.48-5.655 3.33-5.658 6.4 1.155 3.35 0.647 6.84-2.101 9.19-2.7176 2.54-1.598 6.28-1.499 9.37-1.3672 2.07-2.1366 3.99-0.335 5.95 0.382 3.55 3.327 5.9 3.349 9.59 1.24 1.94 3.727 1.82 4.997 4.01 3.71 0.31 3.983 5.49 7.517 6.21 3.036 0.99 6.629 0.3 9.365 1.03 2.243 1.82 4.819 3.09 7.643 3.6 3.551 2.26 4.758-3.37 6.907-5.18 0.112-2.83 2.146-3.05 3.509-0.67 3.101 2.11 6.314-1.51 8.537-3.43 2.173-2.37 4.612-4.42 7.032-6.5 3.436-3.88 4.656-9.43 4.464-14.53 0.34-3.2-2.635-3.38-4.591-3.74 0.885-2.69 3.113-6.54-1.433-6.83-2.607-0.68-8.517-3.6-5.132-6.66 2.498-2.92-0.94-6.85-2.474-9.49-2.656-2.11-4.199-5.06-5.851-7.63-3.197-0.51-6.194-2.45-7.009-5.84-0.854-2.7-0.237-0.7 0.033 0.61" fill-rule="evenodd" stroke="#000" stroke-width=".8136" fill="#fff"/>
    <path id="path4128" opacity=".095506" d="m20.405 181.85c-1.601-1.97 4.721-1.05 4.199-3.01 0.907-2.28-0.178-2.38-0.881-3.63-4.194 3.43-3.206-4.71-6.314 0.02 1.652-0.37 1.381-6.34-0.425-4.55-3.401 1.69-2.681-5.81-2.684-2.74 1.155 3.35 0.647 6.84-2.101 9.19-2.7176 2.54-1.598 6.28-1.499 9.37-1.3672 2.07-2.1366 3.99-0.335 5.95 0.382 3.55 3.327 5.9 3.349 9.59 1.24 1.94 3.727 1.82 4.997 4.01 3.71 0.31 3.983 5.49 7.517 6.21 3.036 0.99 6.629 0.3 9.365 1.03 2.243 1.82 4.819 3.09 7.643 3.6 3.551 2.26 4.758-3.37 6.907-5.18 0.112-2.83 2.146-3.05 3.509-0.67 3.101 2.11 6.314-1.51 8.537-3.43 2.173-2.37-8.346 0.36-5.926-1.72 3.436-3.88-7.752 5.42-7.945 0.31 0.341-3.2-12.37 4.07-9.678-1.55 0.884-2.69 1.536-0.75-3.01-1.04-2.607-0.68-9.804-5.49-6.419-8.56 2.498-2.92-1.342 0.46-2.876-2.18-2.656-2.11-0.959-0.95-2.611-3.52-3.198-0.51-1.792-1.82-2.607-5.21-1.383 3.98-0.982-3.61-0.712-2.29z" fill-rule="evenodd"/>
    <path id="path5880" d="m157.67 192.36s13.14-33.51 16.3-46.88c2.96-12.51 2.58-31.6-1.85-35.14-4.43-3.53-10.25 2.58-10.86 9.82s-1.13 9.06 1.84 22.87c1.35 6.25 0.68 21.09-1.15 28.09s-5.83 22.95-4.28 21.24z" fill-opacity=".22346" fill-rule="evenodd"/>
  </g>
  <metadata>
    <rdf:RDF>
      <cc:Work>
        <dc:format>image/svg+xml</dc:format>
        <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage"/>
        <cc:license rdf:resource="http://creativecommons.org/licenses/publicdomain/"/>
        <dc:publisher>
          <cc:Agent rdf:about="http://openclipart.org/">
            <dc:title>Openclipart</dc:title>
          </cc:Agent>
        </dc:publisher>
      </cc:Work>
      <cc:License rdf:about="http://creativecommons.org/licenses/publicdomain/">
        <cc:permits rdf:resource="http://creativecommons.org/ns#Reproduction"/>
        <cc:permits rdf:resource="http://creativecommons.org/ns#Distribution"/>
        <cc:permits rdf:resource="http://creativecommons.org/ns#DerivativeWorks"/>
      </cc:License>
    </rdf:RDF>
  </metadata>
</svg>
`;
const CHRISTMAS_FOOTER_SVG = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%" height="100%" viewBox="0 0 650 520" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:1.5;">
    <g>
        <rect x="0" y="0" width="650" height="520" style="fill:none;"/>
        <g transform="matrix(1,0,0,1,411.879,150.039)">
            <g id="figure-right" transform="matrix(1,-0,-0,1,-411.879,-150.039)">
                <use xlink:href="#_Image1" x="401.451" y="138.611" width="193px" height="382px"/>
            </g>
            <g id="S" transform="matrix(1.040496,0,0,1.040496,-443.590254,-232.273604)">
                <path d="M474.195,300.941L473.195,239.25C473.195,229.178 481.372,221 491.445,221L525.75,221C535.822,221 533,232.178 533,242.25L534,299.104C546.818,301.925 561.867,301.356 572,307L572,381.728C501.213,360.336 477.442,374.122 479.582,385.81C482.027,399.164 498.599,406.925 520,409.117C555.573,412.759 597.433,433.886 583,511C568.998,585.807 471.978,573.469 429.156,556C427.783,555.44 426.615,479.356 429.156,480.35C517.474,514.907 532.62,488.281 529.389,482.961C519.099,466.016 441.561,477.177 430.156,412C428.922,404.948 427.374,390.449 430.156,358C432.877,326.252 450.72,310.312 474.195,300.941Z" style="fill:none;stroke:black;stroke-width:5.29px;"/>
            </g>
            <animateTransform id="anim-1" attributeName="transform" attributeType="XML" type="rotate" additive="sum" dur="6.2s" begin="indefinite" restart="always" repeatCount="1" calcMode="spline" keyTimes="0;0.045;0.145;0.305;0.475;0.645;0.79;0.9;1" values="0 81.86827 37.822;-14.8 81.86827 37.822;10.2 81.86827 37.822;-6.9 81.86827 37.822;4.2 81.86827 37.822;-2.4 81.86827 37.822;1.2 81.86827 37.822;-0.45 81.86827 37.822;0 81.86827 37.822" keySplines="0.18 0.9 0.28 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.2 0.8 0.3 1" fill="freeze"/>
        </g>
        <g transform="matrix(1,0,0,1,223.377,158.039)">
            <g id="figure-middle" transform="matrix(1,-0,-0,1,-223.377,-158.039)">
                <use xlink:href="#_Image2" x="211.949" y="146.611" width="194px" height="328px"/>
            </g>
            <g id="T2" transform="matrix(0.954355,0,0,1.167487,-51.315749,-257.522582)">
                <path d="M102.809,345.38L74.545,345.38C55.462,345.38 55.606,344.356 55.606,327.619L55.606,298.031C55.606,281.244 55.098,283.459 74.545,283.459L111.531,283.459L111.531,236.784C111.531,228.313 123.564,221.435 133.222,221.435L157.319,221.435C166.978,221.435 176.915,228.313 176.915,236.784L176.915,283.459L208.802,283.459C226.925,283.459 227.74,282.135 227.74,298.031L227.74,327.619C227.74,344.356 227.884,345.38 208.802,345.38L179.096,345.38L179.096,463.651C179.096,479.692 179.884,479 161.596,479L120.309,479C102.979,479 102.809,478.851 102.809,463.651L102.809,345.38Z" style="fill:none;stroke:black;stroke-width:5.16px;"/>
            </g>
            <animateTransform id="anim-2" attributeName="transform" attributeType="XML" type="rotate" additive="sum" dur="6.35s" begin="indefinite" restart="always" repeatCount="1" calcMode="spline" keyTimes="0;0.035;0.135;0.295;0.465;0.64;0.79;0.905;1" values="0 86.0 29.822000000000003;-16.1 86.0 29.822000000000003;11.4 86.0 29.822000000000003;-7.6 86.0 29.822000000000003;4.6 86.0 29.822000000000003;-2.7 86.0 29.822000000000003;1.35 86.0 29.822000000000003;-0.5 86.0 29.822000000000003;0 86.0 29.822000000000003" keySplines="0.16 0.92 0.28 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.2 0.8 0.3 1" fill="freeze"/>
        </g>
        <g transform="matrix(1,0,0,1,40.622929,159.039)">
            <g id="figure-left" transform="matrix(1,-0,-0,1,-40.622929,-159.039)">
                <use xlink:href="#_Image3" x="29.195" y="147.611" width="192px" height="284px"/>
            </g>
            <g id="T1" transform="matrix(1.012299,0,0,0.970857,-59.626917,-209.078268)">
                <path d="M106.131,364.403L79.911,364.403C62.128,364.403 60.973,360.792 60.973,342.593L60.973,311.75C60.973,291.204 61.081,289.94 79.911,289.94L109.273,289.94L109.273,234.676C109.273,224.604 118.102,216.426 127.76,216.426L153.217,216.426C162.875,216.426 172.692,224.604 172.692,234.676L172.692,289.94C172.692,289.94 170.717,289.94 202.26,289.94C221.288,289.94 221.198,292.276 221.198,311.75L221.198,342.593C221.198,361.864 221.09,364.403 202.26,364.403L176.881,364.403L176.881,460.75C176.881,479.208 175.442,479 157.406,479L124.619,479C108.677,479 106.131,477.065 106.131,460.75L106.131,364.403Z" style="fill:none;stroke:black;stroke-width:5.55px;"/>
            </g>
            <animateTransform id="anim-3" attributeName="transform" attributeType="XML" type="rotate" additive="sum" dur="6.5s" begin="indefinite" restart="always" repeatCount="1" calcMode="spline" keyTimes="0;0.055;0.165;0.33;0.5;0.665;0.81;0.915;1" values="0 85.0 28.822000000000003;-13.6 85.0 28.822000000000003;9.3 85.0 28.822000000000003;-6.2 85.0 28.822000000000003;3.7 85.0 28.822000000000003;-2.2 85.0 28.822000000000003;1.05 85.0 28.822000000000003;-0.4 85.0 28.822000000000003;0 85.0 28.822000000000003" keySplines="0.18 0.9 0.28 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.2 0.8 0.3 1" fill="freeze"/>
        </g>
        <g transform="matrix(1.002499,0,0,1.004163,11.989061,5.834789)">
            <g id="CHIME" transform="matrix(0.997508,-0,-0,0.995855,-11.95918,-5.810602)">
                <use xlink:href="#_Image4" x="10.378" y="4.026" width="607px" height="184px"/>
            </g>
        </g>
    </g>
    <rect id="click-target" x="0" y="0" width="650" height="520" fill="transparent" pointer-events="all" tabindex="0" role="button" aria-label="Play animation"/>
    <style><![CDATA[
        svg, #click-target { cursor: pointer; }
        #click-target:focus { outline: none; }
    ]]></style>
    <script><![CDATA[
        (function () {
            const root = document.documentElement;
            const target = document.getElementById('click-target');
            const animations = Array.from(document.querySelectorAll('animateTransform'));
            function play(event) {
                if (event) event.preventDefault();
                root.setCurrentTime(0);
                animations.forEach(function (animation) {
                    try { animation.beginElement(); } catch (_) {}
                });
            }
            target.addEventListener('click', play);
            target.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' || event.key === ' ') play(event);
            });
        }());
    ]]></script>
    <defs>
        <image id="_Image1" width="193px" height="382px" xlink:href="data:image/png;base64,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"/>
        <image id="_Image2" width="194px" height="328px" xlink:href="data:image/png;base64,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"/>
        <image id="_Image3" width="192px" height="284px" xlink:href="data:image/png;base64,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"/>
        <image id="_Image4" width="607px" height="184px" xlink:href="data:image/png;base64,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"/>
    </defs>
</svg>
`;

const ICONS = {
  chevron: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M8.12 9.29a1 1 0 0 1 1.41 0L12 11.76l2.47-2.47a1 1 0 1 1 1.41 1.41l-3.18 3.18a1 1 0 0 1-1.41 0L8.12 10.7a1 1 0 0 1 0-1.41z"/>
    </svg>
  `,
  pencil: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M3 17.25V21h3.75L17.8 9.94l-3.75-3.75L3 17.25zm2.92 2.33H5v-.92l9.06-9.06.92.92L5.92 19.58zM20.71 7.04a1.003 1.003 0 0 0 0-1.42L18.37 3.29a1.003 1.003 0 0 0-1.42 0l-1.13 1.13 3.75 3.75 1.14-1.13z"/>
    </svg>
  `,
  trash: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M6 19c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V7H6v12zm3.46-7.88 1.41-1.41L12 10.83l1.12-1.12 1.41 1.41L13.41 12l1.12 1.12-1.41 1.41L12 13.41l-1.12 1.12-1.41-1.41L10.59 12l-1.13-1.12zM15.5 4l-1-1h-5l-1 1H5v2h14V4z"/>
    </svg>
  `,
  check: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
    </svg>
  `,
  alert: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
    </svg>
  `,
  repeat: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M17 17H7v3l-4-4 4-4v3h8a3 3 0 0 0 0-6H9v2H7V7h8a5 5 0 1 1 0 10zm0-14 4 4-4 4V8H9a3 3 0 1 0 0 6h6v2H9a5 5 0 1 1 0-10h8V3z"/>
    </svg>
  `,
  broom: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M18.16 3.47 19.58 4.89 15.12 9.35 13.7 7.93l4.46-4.46zm-5.07 5.88 2.12 2.12-5.7 5.7c-.35.36-.8.6-1.29.7l-3.37.73.73-3.37c.11-.49.35-.94.7-1.29l6.81-6.59zm-7.7 10.93h13.86v1.5H5.39z"/>
    </svg>
  `,
  beaker: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path
        d="M9 3h6v2l-1.2 1.9v3.15l4.53 7.18A2.3 2.3 0 0 1 16.39 21H7.61a2.3 2.3 0 0 1-1.94-3.77l4.53-7.18V6.9L9 5V3Z"
        fill="none"
        stroke="currentColor"
        stroke-width="1.7"
        stroke-linejoin="round"
      />
      <path
        d="M8.15 15.2c1.1-.6 2.13-.4 3.1 0 .98.4 1.9.8 3.1.2.72-.34 1.28-.32 1.82-.1l1.27 2a.92.92 0 0 1-.78 1.4H7.32a.92.92 0 0 1-.78-1.4l1.61-2.56Z"
        fill="#22c55e"
        opacity="0.95"
      />
      <circle cx="10" cy="12.2" r="0.95" fill="#bbf7d0"/>
      <circle cx="12.8" cy="13.2" r="0.72" fill="#dcfce7"/>
      <circle cx="14.9" cy="11.45" r="0.58" fill="#bbf7d0"/>
    </svg>
  `,
  run: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M14.5 4.2a1.9 1.9 0 1 1-3.8 0 1.9 1.9 0 0 1 3.8 0Zm-2.8 4.35 2.05.55 1.45-1.5a1.15 1.15 0 1 1 1.65 1.6l-1.95 2a1.15 1.15 0 0 1-1.12.3l-1.28-.34-1.25 2.2 1.82 1.56 2.16-.02a1.15 1.15 0 1 1 .02 2.3l-2.58.03a1.15 1.15 0 0 1-.76-.28l-2.72-2.33a1.15 1.15 0 0 1-.26-1.42l1.57-2.78-1.7-.46-1.37 1.1a1.15 1.15 0 0 1-1.44-1.8l1.83-1.47a1.15 1.15 0 0 1 1.04-.22l2.25.6a1.2 1.2 0 0 1 .28.12Zm-2.05 8.3a1.15 1.15 0 0 1 1.6.26l1.65 2.35a1.15 1.15 0 1 1-1.88 1.32l-1.65-2.34a1.15 1.15 0 0 1 .28-1.6Z"/>
    </svg>
  `,
  folder: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M10 4l2 2h8a2 2 0 0 1 2 2v8.5A3.5 3.5 0 0 1 18.5 20h-13A3.5 3.5 0 0 1 2 16.5V7a3 3 0 0 1 3-3h5z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
    </svg>
  `,
  file: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M7 3h7l5 5v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
      <path d="M14 3v5h5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
    </svg>
  `,
  music: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M4 10h4.2l5-4.2c.65-.54 1.8-.1 1.8.76v10.88c0 .86-1.15 1.3-1.8.76l-5-4.2H4a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1z" fill="currentColor"/>
      <path d="M17.2 9.1a1 1 0 0 1 1.41 0 4.54 4.54 0 0 1 0 6.4 1 1 0 1 1-1.41-1.42 2.54 2.54 0 0 0 0-3.56 1 1 0 0 1 0-1.42z" fill="currentColor"/>
      <path d="M19.96 6.34a1 1 0 0 1 1.41 0 8.45 8.45 0 0 1 0 11.94 1 1 0 0 1-1.41-1.42 6.45 6.45 0 0 0 0-9.1 1 1 0 0 1 0-1.42z" fill="currentColor"/>
    </svg>
  `,
  upload: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M12 16V5M8 9l4-4 4 4" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M5 19h14" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>
    </svg>
  `,
  plus: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M12 5v14M5 12h14" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>
    </svg>
  `,
  refresh: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M20 11a8 8 0 1 0 2.1 5.4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      <path d="M20 4v7h-7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `,
  more: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <circle cx="6" cy="12" r="1.8" />
      <circle cx="12" cy="12" r="1.8" />
      <circle cx="18" cy="12" r="1.8" />
    </svg>
  `,
  moreVertical: `
    <svg preserveAspectRatio="xMidYMid meet" focusable="false" role="img" aria-hidden="true" viewBox="0 0 24 24">
      <g>
        <path class="primary-path" d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"></path>
      </g>
    </svg>
  `,
  close: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M6 6l12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>
    </svg>
  `,
  play: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M8 6.5v11l9-5.5-9-5.5z" fill="currentColor"/>
    </svg>
  `,
  pause: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M8 6h3v12H8zm5 0h3v12h-3z" fill="currentColor"/>
    </svg>
  `,
  stop: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <rect x="7" y="7" width="10" height="10" rx="1" fill="currentColor"/>
    </svg>
  `,
};
const OPTION_ICON_DATA_URLS = {
  "add_cover_art": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Crect%20x=%2214%22%20y=%2216%22%20width=%2222%22%20height=%2222%22%20rx=%226%22%20fill=%22%2303a9f4%22/%3E%0A%20%20%3Ccircle%20cx=%2225%22%20cy=%2227%22%20r=%224%22%20fill=%22%23fff%22/%3E%0A%20%20%3Cpath%20d=%22M42%2022h8M42%2030h10M42%2038h6%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M18%2044c3-3%205-4%207-4s4%201%207%204%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "crossfade": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M16%2042c3-10%206-16%209-16s6%206%209%2016%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M30%2042c3-10%206-16%209-16s6%206%209%2016%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M28%2023h8%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "custom_chimes_path": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M12%2021h14l4%204h20v18c0%203-2%205-5%205H17c-3%200-5-2-5-5V21z%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Ccircle%20cx=%2222%22%20cy=%2238%22%20r=%223.5%22%20fill=%22%23f472b6%22/%3E%0A%20%20%3Crect%20x=%2228%22%20y=%2234%22%20width=%228%22%20height=%228%22%20rx=%222.5%22%20fill=%22%2303a9f4%22/%3E%0A%20%20%3Cpath%20d=%22M44%2035l3%206h-6l3-6z%22%20fill=%22%23facc15%22/%3E%0A%20%20%3Cpath%20d=%22M38%2018l1.2%202.6%202.8.4-2%201.9.5%202.8-2.5-1.4-2.5%201.4.5-2.8-2-1.9%202.8-.4L38%2018z%22%20fill=%22%2322c55e%22/%3E%0A%3C/svg%3E",
  "default_language_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M21%2020h10M26%2020v24M16%2031h20%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M37%2039c3-2%205-5%206-9%201%204%203%207%206%209%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M41%2045h12%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "default_tld_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Ccircle%20cx=%2226%22%20cy=%2232%22%20r=%2212%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M14%2032h24M26%2020c-3%204-4%208-4%2012s1%208%204%2012M26%2020c3%204%204%208%204%2012s-1%208-4%2012%22%20stroke=%22%237dd3fc%22%20stroke-width=%222.5%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M43%2024h9M43%2032h7M43%2040h9%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "default_voice_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Crect%20x=%2225%22%20y=%2218%22%20width=%2214%22%20height=%2222%22%20rx=%227%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M20%2032c0%207%205%2012%2012%2012s12-5%2012-12%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M32%2044v6%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M24%2050h16%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "fade_transition_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M17%2042V22%22%20stroke=%22%237ea6b7%22%20stroke-width=%224%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M26%2042V18%22%20stroke=%22%237dd3fc%22%20stroke-width=%224%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M35%2042V25%22%20stroke=%22%2303a9f4%22%20stroke-width=%224%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M44%2042V31%22%20stroke=%22%23d7edf8%22%20stroke-width=%224%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "fallback_tts_platform_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Crect%20x=%2212%22%20y=%2218%22%20width=%2216%22%20height=%2224%22%20rx=%225%22%20stroke=%22%237ea6b7%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M31%2030h9%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M36%2025l5%205-5%205%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Crect%20x=%2242%22%20y=%2218%22%20width=%2210%22%20height=%2224%22%20rx=%225%22%20fill=%22%2303a9f4%22/%3E%0A%3C/svg%3E",
  "offset": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M16%2038c3-6%206-12%209%200s6%2012%209%200%206-12%209%200%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M16%2024h12%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M25%2020l4%204-4%204%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%3C/svg%3E",
  "queue_timeout": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Ccircle%20cx=%2224%22%20cy=%2231%22%20r=%2210%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M24%2024v8l5%203%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M40%2024h10M40%2031h8M40%2038h6%22%20stroke=%22%237ea6b7%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "remove_temp_file_delay": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M24%2019h16%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M27%2019l1%2023c.1%202%201.4%203%203.3%203h5.4c1.9%200%203.2-1%203.3-3l1-23%22%20stroke=%22%237ea6b7%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M29%2019l1.5-3h9L41%2019%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M31%2025v13M37%2025v13%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Ccircle%20cx=%2246%22%20cy=%2218%22%20r=%227%22%20fill=%22%23f59e0b%22/%3E%0A%20%20%3Cpath%20d=%22M46%2015v3l2%201%22%20stroke=%22%23fff%22%20stroke-width=%222.5%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%3C/svg%3E",
  "temp_chimes_path": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M12%2021h15l4%204h21v18c0%203-2%205-5%205H17c-3%200-5-2-5-5V21z%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M32%2029v10%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M27%2035l5%205%205-5%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M25%2043h14%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "temp_path": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M12%2021h15l4%204h21v18c0%203-2%205-5%205H17c-3%200-5-2-5-5V21z%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M29%2028h8v5l-2%202%202%202v5h-8v-5l2-2-2-2v-5z%22%20stroke=%22%23d7edf8%22%20stroke-width=%222.8%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M29%2033h8%22%20stroke=%22%237dd3fc%22%20stroke-width=%222.8%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "tts_platform_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Crect%20x=%2212%22%20y=%2218%22%20width=%2218%22%20height=%2228%22%20rx=%226%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Crect%20x=%2235%22%20y=%2218%22%20width=%2218%22%20height=%2210%22%20rx=%225%22%20fill=%22%2303a9f4%22/%3E%0A%20%20%3Crect%20x=%2235%22%20y=%2232%22%20width=%2218%22%20height=%226%22%20rx=%223%22%20fill=%22%237ea6b7%22/%3E%0A%20%20%3Crect%20x=%2235%22%20y=%2242%22%20width=%2214%22%20height=%226%22%20rx=%223%22%20fill=%22%237ea6b7%22/%3E%0A%3C/svg%3E",
  "tts_timeout": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M17%2024h18%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M26%2024v16%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M21%2040h10%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Ccircle%20cx=%2244%22%20cy=%2231%22%20r=%2210%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M44%2026v6l4%203%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%3C/svg%3E",
  "www_path": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M12%2021h15l4%204h21v18c0%203-2%205-5%205H17c-3%200-5-2-5-5V21z%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Ccircle%20cx=%2236%22%20cy=%2238%22%20r=%227%22%20stroke=%22%23d7edf8%22%20stroke-width=%222.6%22/%3E%0A%20%20%3Cpath%20d=%22M29%2038h14M36%2031c-1.6%202-2.4%204.3-2.4%207s.8%205%202.4%207M36%2031c1.6%202%202.4%204.3%202.4%207s-.8%205-2.4%207%22%20stroke=%22%237dd3fc%22%20stroke-width=%222.2%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
};

const template = document.createElement("template");
template.innerHTML = `
  <style>
    ${EMPTY_CHIME_SET_SLOT_MACHINE_STYLES}
    :host {
      box-sizing: border-box;
      display: block;
      position: relative;
      isolation: isolate;
      min-height: 100%;
      color: var(--primary-text-color);
    }

    .snowfall {
      position: fixed;
      z-index: 0;
      inset: 0;
      overflow: hidden;
      pointer-events: none;
    }

    .snowflake-particle {
      position: absolute;
      top: -12vh;
      left: var(--snow-left);
      width: var(--snow-size);
      height: var(--snow-size);
      color: #68bfe8;
      opacity: var(--snow-opacity);
      filter: drop-shadow(0 0 2px rgba(72, 158, 201, 0.62));
      animation: snowfall var(--snow-duration) linear var(--snow-delay) infinite;
    }

    .snowflake-particle svg {
      display: block;
      width: 100%;
      height: 100%;
    }

    @keyframes snowfall {
      from { transform: translate3d(0, -8vh, 0) rotate(0deg); }
      to { transform: translate3d(var(--snow-drift), 120vh, 0) rotate(240deg); }
    }

    @media (prefers-reduced-motion: reduce) {
      .snowflake-particle { animation: none; }
    }

    *,
    *::before,
    *::after {
      box-sizing: inherit;
    }

    a {
      color: var(--primary-color);
    }

    :host {
      --panel-safe-area-top: env(safe-area-inset-top, 0px);
      --panel-safe-area-right: env(safe-area-inset-right, 0px);
      --panel-safe-area-bottom: env(safe-area-inset-bottom, 0px);
      --panel-safe-area-left: env(safe-area-inset-left, 0px);
    }

    .layout {
      position: relative;
      z-index: 1;
      /* Field variants can add a textarea after the browser has selected an
       * anchor below this panel. Keep that layout growth from moving the page. */
      overflow-anchor: none;
      max-width: 1180px;
      margin: 0 auto;
      padding:
        24px
        calc(24px + var(--panel-safe-area-right))
        calc(24px + var(--panel-safe-area-bottom))
        calc(24px + var(--panel-safe-area-left));
      display: flex;
      flex-direction: column;
      gap: 0;
    }

    .topbar-wrap {
      --topbar-background: color-mix(in srgb, var(--card-background-color) 72%, transparent);
      position: sticky;
      top: 0;
      z-index: 10;
      width: 100%;
      overflow: hidden;
      padding-top: var(--panel-safe-area-top);
      backdrop-filter: blur(14px);
      background: var(--topbar-background);
      border-bottom: 1px solid color-mix(in srgb, var(--divider-color) 86%, transparent);
      isolation: isolate;
    }

    .topbar-wrap::before {
      content: "";
      position: absolute;
      z-index: -1;
      top: -100vh;
      right: 0;
      bottom: 0;
      left: 0;
      background: var(--topbar-background);
      pointer-events: none;
    }

    .topbar {
      position: relative;
      width: 100%;
      margin: 0;
      height: 56px;
      padding:
        0
        calc(24px + var(--panel-safe-area-right))
        0
        calc(24px + var(--panel-safe-area-left));
      display: flex;
      align-items: center;
      justify-content: flex-start;
      gap: 16px;
    }

    .topbar-notice {
      padding:
        0
        calc(24px + var(--panel-safe-area-right))
        12px
        calc(24px + var(--panel-safe-area-left));
    }

    .topbar-notice-inner {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      min-height: 32px;
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, var(--warning-color, #f59e0b) 36%, transparent);
      background: color-mix(in srgb, var(--warning-color, #f59e0b) 12%, transparent);
      color: var(--primary-text-color);
      font-size: 0.88rem;
      line-height: 1.35;
    }

    .topbar-notice-label {
      font-weight: 700;
      white-space: nowrap;
    }

    .topbar-main {
      position: relative;
      z-index: 1;
      display: flex;
      align-items: center;
      min-width: 0;
      flex: 1 1 auto;
      margin-left: 0;
    }

    .topbar-nav {
      display: none;
      align-items: center;
      gap: 10px;
      flex: 0 0 auto;
    }

    .topbar-menu {
      display: inline-flex;
      min-height: 40px;
      min-width: 40px;
      padding: 0;
      border-radius: 999px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--primary-text-color);
      box-shadow: none;
      line-height: 1;
    }

    .topbar-menu svg {
      width: 22px;
      height: 22px;
      fill: currentColor;
      display: block;
    }

    .topbar-menu:hover,
    .topbar-menu:focus-visible {
      border-color: var(--divider-color);
      background: color-mix(in srgb, var(--card-background-color) 88%, white 12%);
    }

    .topbar-actions {
      position: relative;
      z-index: 1;
      display: flex;
      align-items: center;
      gap: 14px;
      flex: 0 0 auto;
      margin-left: 0;
    }

    .topbar-text {
      min-width: 0;
    }

    .topbar-title {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 400;
      color: var(--primary-text-color);
      line-height: 1;
      letter-spacing: -0.012em;
      display: flex;
      align-items: center;
      flex-wrap: wrap;
    }

    .topbar-title-brand {
      position: relative;
      display: inline-block;
    }

    .topbar-santa-hat {
      position: absolute;
      z-index: 1;
      width: 19px;
      height: 13px;
      top: -5px;
      left: -8px;
      pointer-events: none;
      transform: rotate(-10deg);
      filter: drop-shadow(0 0 1px #000);
    }

    .topbar-santa-hat svg {
      display: block;
      width: 100%;
      height: 100%;
    }

    .topbar-beta-badge {
      position: absolute;
      right: -43px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 5px;
      border-radius: 10px;
      background: #c62828;
      color: #fff !important;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      line-height: 1;
      user-select: none;
    }

    .topbar-beta-badge:focus-visible {
      outline: 2px solid var(--primary-color);
      outline-offset: 3px;
    }

    .topbar-beta-badge.is-shaking {
      animation: beta-badge-shake 200ms ease-in-out;
    }

    .topbar-beta-bug {
      position: fixed;
      z-index: 20;
      left: var(--beta-bug-left);
      top: var(--beta-bug-top);
      width: 22px;
      height: 14px;
      display: grid;
      place-items: center;
      pointer-events: none;
      transform-origin: center;
      animation:
        beta-bug-fall 120ms ease-in forwards,
        beta-bug-land 180ms linear 120ms forwards,
        beta-bug-crawl 2200ms linear 300ms forwards,
        beta-bug-wiggle 180ms ease-in-out 300ms infinite;
    }

    .topbar-beta-bug svg {
      display: block;
      width: 100%;
      height: 100%;
      transform-origin: center;
      animation: beta-bug-run-turn 300ms ease-in-out 300ms infinite;
    }

    @keyframes beta-badge-shake {
      0%, 100% { transform: translateX(0); }
      25% { transform: translateX(-2px) rotate(-3deg); }
      75% { transform: translateX(2px) rotate(3deg); }
    }

    @keyframes beta-bug-fall {
      from { transform: translateY(0); }
      to { transform: translateY(var(--beta-bug-drop)); }
    }

    @keyframes beta-bug-land {
      0% {
        transform: translateY(var(--beta-bug-drop));
        animation-timing-function: ease-out;
      }
      50% {
        transform: translateY(calc(var(--beta-bug-drop) - 3px));
        animation-timing-function: ease-in;
      }
      100% { transform: translateY(var(--beta-bug-drop)); }
    }

    @keyframes beta-bug-crawl {
      0% { transform: translateY(var(--beta-bug-drop)); }
      100% { transform: translate(var(--beta-bug-crawl), var(--beta-bug-drop)); }
    }

    @keyframes beta-bug-wiggle {
      0%, 100% { width: 22px; }
      50% { width: 20.9px; }
    }

    @keyframes beta-bug-run-turn {
      0%, 100% { transform: rotate(0deg); }
      25% { transform: rotate(-10deg); }
      50% { transform: rotate(0deg); }
      75% { transform: rotate(10deg); }
    }

    .section {
      border: 1px solid var(--divider-color);
      border-radius: 24px;
      // background: color-mix(in srgb, var(--card-background-color) 92%, white 8%);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
    }

    .section p,
    .hint,
    .message {
      margin: 0;
      color: var(--secondary-text-color);
      line-height: 1.6;
    }

    button {
      appearance: none;
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      transition: transform 120ms ease, opacity 120ms ease, box-shadow 120ms ease;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    a.button-secondary,
    a.button-primary {
      appearance: none;
      border-radius: 999px;
      padding: 12px 18px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      transition: transform 120ms ease, opacity 120ms ease, box-shadow 120ms ease;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    button:hover {
      transform: translateY(-1px);
    }

    a.button-secondary:hover,
    a.button-primary:hover {
      transform: translateY(-1px);
      text-decoration: none;
    }

    button:disabled {
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }

    .button-primary {
      color: var(--text-primary-color, #fff);
      background: linear-gradient(135deg, var(--primary-color), color-mix(in srgb, var(--primary-color) 72%, black 28%));
      box-shadow: 0 16px 28px rgba(3, 169, 244, 0.28);
    }

    .button-secondary {
      color: var(--primary-text-color);
      background: color-mix(in srgb, var(--card-background-color) 88%, white 12%);
      border: 1px solid var(--divider-color);
      box-shadow: none;
    }

    .button-restart {
      color: #fff;
      background: color-mix(in srgb, var(--error-color, #d32f2f) 70%, black 30%);
      border: 1px solid color-mix(in srgb, var(--error-color, #d32f2f) 72%, white 28%);
      box-shadow: 0 0 0 0 color-mix(in srgb, var(--error-color, #d32f2f) 0%, transparent);
      animation: restartPulse 1s ease-in-out infinite;
    }

    .save-slot {
      width: 80px;
      flex: 0 0 80px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    .save-slot .button-primary {
      width: 100%;
    }

    .button-primary:disabled:not(.is-saving) {
      background: transparent;
      color: color-mix(in srgb, var(--primary-text-color) 88%, transparent);
    }

    .save-status {
      width: 100%;
      height: 40px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      font-weight: 700;
      line-height: 1;
      border: 1px solid transparent;
    }

    .save-status.success {
      color: var(--primary-color);
      background: color-mix(in srgb, var(--primary-color) 12%, transparent);
      border-color: color-mix(in srgb, var(--primary-color) 28%, transparent);
    }

    .save-status.error {
      color: var(--error-color, #d32f2f);
      background: color-mix(in srgb, var(--error-color, #d32f2f) 10%, transparent);
      border-color: color-mix(in srgb, var(--error-color, #d32f2f) 24%, transparent);
    }

    .button-spinner {
      width: 16px;
      height: 16px;
      border-radius: 999px;
      border: 2px solid rgba(255, 255, 255, 0.28);
      border-top-color: rgba(255, 255, 255, 0.95);
      animation: buttonSpin 0.8s linear infinite;
    }

    .notify-profile-actions .button-primary .button-spinner {
      border-color: color-mix(in srgb, var(--primary-color) 28%, transparent);
      border-top-color: var(--primary-color);
    }

    @keyframes restartPulse {
      0%,
      100% {
        border-color: color-mix(in srgb, var(--error-color, #d32f2f) 35%, transparent);
        box-shadow: 0 0 0 0 color-mix(in srgb, var(--error-color, #d32f2f) 0%, transparent);
      }

      50% {
        border-color: color-mix(in srgb, var(--error-color, #d32f2f) 90%, white 10%);
        box-shadow: 0 0 0 2px color-mix(in srgb, var(--error-color, #d32f2f) 28%, transparent);
      }
    }

    @keyframes buttonSpin {
      from {
        transform: rotate(0deg);
      }

      to {
        transform: rotate(360deg);
      }
    }

    .topbar-link {
      color: var(--primary-color);
      font: inherit;
      font-weight: 600;
      text-decoration: none;
      white-space: nowrap;
    }

    .topbar-link:hover {
      text-decoration: underline;
    }

    .message {
      margin: 18px;
      padding: 16px 18px;
      border-radius: 18px;
      border: 1px solid;
    }

    .message.success {
      border-color: rgba(56, 142, 60, 0.35);
      background: rgba(56, 142, 60, 0.08);
      color: var(--primary-text-color);
    }

    .message.error {
      border-color: rgba(211, 47, 47, 0.35);
      background: rgba(211, 47, 47, 0.08);
      color: var(--primary-text-color);
    }

    .transient-banner-region {
      position: relative;
      z-index: 11;
      height: 0;
      overflow: visible;
    }

    .transient-banner {
      position: absolute;
      top: 12px;
      right: calc(24px + var(--panel-safe-area-right));
      left: calc(24px + var(--panel-safe-area-left));
      margin: 0;
      padding: 14px 18px;
      border: 1px solid rgba(211, 47, 47, 0.4);
      border-radius: 14px;
      background: color-mix(in srgb, var(--card-background-color) 92%, #d32f2f 8%);
      color: var(--primary-text-color);
      box-shadow: 0 10px 28px rgba(0, 0, 0, 0.18);
    }

    .panel-alerts {
      display: flex;
      flex-direction: column;
      gap: 14px;
      margin-bottom: 18px;
    }

    .panel-alert {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      padding: 18px 20px;
      border-radius: 20px;
      border: 1px solid;
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
    }

    .panel-alert.warning {
      border-color: color-mix(in srgb, var(--warning-color, #f59e0b) 62%, var(--divider-color) 38%);
      background:
        linear-gradient(
          135deg,
          color-mix(in srgb, var(--warning-color, #f59e0b) 22%, var(--card-background-color) 78%),
          color-mix(in srgb, var(--warning-color, #f59e0b) 10%, var(--card-background-color) 90%)
        );
      color: var(--primary-text-color);
    }

    .panel-alert.error {
      border-color: color-mix(in srgb, #d32f2f 55%, transparent);
      background: linear-gradient(135deg, rgba(244, 67, 54, 0.18), rgba(255, 235, 238, 0.9));
      color: var(--primary-text-color);
    }

    .panel-alert-copy {
      display: flex;
      align-items: flex-start;
      gap: 14px;
      min-width: 0;
      flex: 1 1 auto;
    }

    .panel-alert-icon {
      width: 35px;
      height: 35px;
      flex: 0 0 35px;
      margin-top: 2px;
      color: currentColor;
    }

    .panel-alert-icon svg {
      width: 100%;
      height: 100%;
      display: block;
      fill: currentColor;
    }

    .panel-alert-text {
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 0;
    }

    .panel-alert-title {
      margin: 0;
      font-size: 1rem;
      font-weight: 800;
      color: var(--primary-text-color);
    }

    .panel-alert-message {
      margin: 0;
      color: var(--primary-text-color);
      line-height: 1.55;
    }

    .panel-alert-message strong {
      font-weight: 800;
      color: var(--primary-text-color);
    }

    .panel-alert-action {
      flex: 0 0 auto;
      align-self: center;
      white-space: nowrap;
    }

    .panel-alert.warning .panel-alert-action.button-secondary {
      color: var(--primary-text-color);
      background: color-mix(in srgb, var(--warning-color, #f59e0b) 18%, var(--card-background-color) 82%);
      border-color: color-mix(in srgb, var(--warning-color, #f59e0b) 48%, var(--divider-color) 52%);
    }

    .panel-alert.error .panel-alert-action.button-primary {
      background: linear-gradient(135deg, #d32f2f, color-mix(in srgb, #d32f2f 76%, black 24%));
      box-shadow: 0 16px 28px rgba(211, 47, 47, 0.24);
    }

    @media (max-width: 760px) {
      .panel-alert {
        flex-direction: column;
        align-items: stretch;
      }

      .panel-alert-action {
        align-self: flex-start;
      }
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .chapter-group {
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .chapter-group + .chapter-group {
      margin-top: 18px;
    }

    .chapter-workspace {
      display: flex;
      flex-direction: column;
    }

    @media (prefers-color-scheme: light) {
      .topbar-wrap {
        // background: color-mix(in srgb, var(--card-background-color) 92%, white 8%);
      }

      .section {
        background: color-mix(in srgb, var(--card-background-color) 97%, white 3%);
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
      }

      .chapter-hero {
        background:
          radial-gradient(circle at top right, color-mix(in srgb, var(--primary-color) 10%, transparent), transparent 42%),
          linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 98%, white 2%), color-mix(in srgb, white 92%, #f8fbff 8%));
      }

      .notify-workspace .chapter-hero {
        background:
          radial-gradient(circle at top right, color-mix(in srgb, #dc2626 12%, transparent), transparent 44%),
          linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 98%, white 2%), color-mix(in srgb, white 90%, #fff5f6 10%));
      }

      .logs-workspace .chapter-hero {
        background:
          radial-gradient(circle at top right, color-mix(in srgb, #f97316 12%, transparent), transparent 44%),
          linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 98%, white 2%), color-mix(in srgb, white 90%, #fff8de 10%));
      }

      .chapter-hero .section,
      .notify-profile-card,
      .field,
      .log-event-row,
      .picker-preview {
        background: color-mix(in srgb, var(--card-background-color) 97%, white 3%);
      }
    }

    .chapter-hero {
      --chapter-hero-copy-color: color-mix(in srgb, var(--primary-color) 78%, white 22%);
      --chapter-hero-help-border-color: color-mix(in srgb, var(--primary-color) 12%, var(--divider-color));
      --chapter-hero-help-background: color-mix(in srgb, var(--primary-color) 10%, var(--card-background-color));
      --chapter-hero-help-background-hover: color-mix(in srgb, var(--primary-color) 16%, var(--card-background-color));
      padding: 22px 24px;
      border-radius: 24px;
      border: 2px solid color-mix(in srgb, var(--primary-color) 14%, var(--divider-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--primary-color) 14%, transparent), transparent 42%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 94%, white 6%), color-mix(in srgb, var(--secondary-background-color) 78%, transparent));
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.12);
      transition:
        border-color 250ms ease,
        background 250ms ease,
        box-shadow 250ms ease,
        border-radius 250ms ease;
    }

    .configuration-workspace .chapter-hero {
      background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--configuration-accent) 12%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 92%, white 8%), color-mix(in srgb, var(--secondary-background-color) 84%, transparent));
      border-color: color-mix(in srgb, var(--configuration-accent) 32%, var(--divider-color));
      --chapter-hero-help-border-color: color-mix(in srgb, var(--configuration-accent) 32%, var(--divider-color));
      --chapter-hero-help-background: color-mix(in srgb, var(--configuration-accent) 12%, var(--card-background-color));
      --chapter-hero-help-background-hover: color-mix(in srgb, var(--configuration-accent) 18%, var(--card-background-color));
      box-shadow: 0 20px 44px rgba(0, 0, 0, 0.14);
    }
    .configuration-workspace .chapter-hero { --chapter-hero-copy-color: color-mix(in srgb, var(--configuration-accent) 82%, white 18%); }
    .configuration-workspace {
      --configuration-accent: #3f9e63;
      --section-help-color: color-mix(in srgb, var(--configuration-accent) 82%, white 18%);
      --section-help-border: color-mix(in srgb, var(--configuration-accent) 32%, var(--divider-color));
      --section-help-background: color-mix(in srgb, var(--configuration-accent) 12%, var(--card-background-color));
      --section-help-background-hover: color-mix(in srgb, var(--configuration-accent) 18%, var(--card-background-color));
    }

    .chapter-hero-toggle {
      min-width: 0;
      display: block;
      width: calc(100% + 48px);
      margin: -22px -24px;
      padding: 22px 24px;
      cursor: pointer;
      border-radius: 24px;
    }

    .chapter-hero-toggle:focus-visible {
      outline: 2px solid color-mix(in srgb, var(--primary-color) 45%, transparent);
      outline-offset: 6px;
    }

    .notify-workspace .chapter-hero {
      border-color: color-mix(in srgb, #dc2626 28%, var(--divider-color));
      --chapter-hero-help-border-color: color-mix(in srgb, #dc2626 28%, var(--divider-color));
      --chapter-hero-help-background: color-mix(in srgb, #dc2626 12%, var(--card-background-color));
      --chapter-hero-help-background-hover: color-mix(in srgb, #dc2626 18%, var(--card-background-color));
      background: var(--notify-section-surface);
      box-shadow: 0 22px 48px rgba(0, 0, 0, 0.18);
    }

    .notify-workspace .chapter-hero { --chapter-hero-copy-color: color-mix(in srgb, #dc2626 82%, white 18%); }
    .notify-workspace {
      --notify-section-surface:
        radial-gradient(circle at top right, color-mix(in srgb, #dc2626 12%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 97%, #fff4f5 3%), color-mix(in srgb, var(--secondary-background-color) 92%, #fff7f8 8%));
      --section-help-color: color-mix(in srgb, #dc2626 82%, white 18%);
      --section-help-border: color-mix(in srgb, #dc2626 28%, var(--divider-color));
      --section-help-background: color-mix(in srgb, #dc2626 12%, var(--card-background-color));
      --section-help-background-hover: color-mix(in srgb, #dc2626 18%, var(--card-background-color));
    }

    .chime-sets-workspace .chapter-hero {
      border-color: color-mix(in srgb, #7c3aed 32%, var(--divider-color));
      --chapter-hero-help-border-color: color-mix(in srgb, #7c3aed 32%, var(--divider-color));
      --chapter-hero-help-background: color-mix(in srgb, #7c3aed 16%, var(--card-background-color));
      --chapter-hero-help-background-hover: color-mix(in srgb, #7c3aed 22%, var(--card-background-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, #7c3aed 14%, transparent), transparent 42%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 92%, white 8%), color-mix(in srgb, var(--secondary-background-color) 84%, transparent));
    }
    .chime-sets-workspace .chapter-hero { --chapter-hero-copy-color: color-mix(in srgb, #7c3aed 82%, white 18%); }
    .chime-sets-workspace {
      --section-help-color: color-mix(in srgb, #7c3aed 82%, white 18%);
      --section-help-border: color-mix(in srgb, #7c3aed 32%, var(--divider-color));
      --section-help-background: color-mix(in srgb, #7c3aed 16%, var(--card-background-color));
      --section-help-background-hover: color-mix(in srgb, #7c3aed 22%, var(--card-background-color));
    }
    .chime-sets-workspace .chime-sets-chapter-toggle {
      width: 42px;
      min-width: 42px;
      min-height: 42px;
      padding: 0;
      border-radius: 999px;
      border-color: color-mix(in srgb, #7c3aed 30%, var(--divider-color));
      background: color-mix(in srgb, #7c3aed 16%, var(--card-background-color));
      color: color-mix(in srgb, #5b21b6 82%, black 18%);
    }

    .chimes-workspace .chapter-hero {
      border-color: color-mix(in srgb, var(--primary-color) 32%, var(--divider-color));
      --chapter-hero-help-border-color: color-mix(in srgb, var(--primary-color) 32%, var(--divider-color));
      --chapter-hero-help-background: color-mix(in srgb, var(--primary-color) 12%, var(--card-background-color));
      --chapter-hero-help-background-hover: color-mix(in srgb, var(--primary-color) 18%, var(--card-background-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--primary-color) 12%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 94%, white 6%), color-mix(in srgb, var(--secondary-background-color) 78%, transparent));
    }
    .chimes-workspace .chapter-hero { --chapter-hero-copy-color: color-mix(in srgb, var(--primary-color) 82%, white 18%); }
    .chimes-workspace {
      --section-help-color: color-mix(in srgb, var(--primary-color) 82%, white 18%);
      --section-help-border: color-mix(in srgb, var(--primary-color) 32%, var(--divider-color));
      --section-help-background: color-mix(in srgb, var(--primary-color) 12%, var(--card-background-color));
      --section-help-background-hover: color-mix(in srgb, var(--primary-color) 18%, var(--card-background-color));
    }

    .logs-workspace .chapter-hero {
      border-color: color-mix(in srgb, #f97316 32%, var(--divider-color));
      --chapter-hero-help-border-color: color-mix(in srgb, #f97316 32%, var(--divider-color));
      --chapter-hero-help-background: color-mix(in srgb, #f97316 12%, var(--card-background-color));
      --chapter-hero-help-background-hover: color-mix(in srgb, #f97316 18%, var(--card-background-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, #f97316 12%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 97%, #fff8de 3%), color-mix(in srgb, var(--secondary-background-color) 92%, #fffaf0 8%));
    }

    .logs-workspace .chapter-hero { --chapter-hero-copy-color: color-mix(in srgb, #f97316 86%, white 14%); }
    .logs-workspace {
      --section-help-color: color-mix(in srgb, #f97316 86%, white 14%);
      --section-help-border: color-mix(in srgb, #f97316 32%, var(--divider-color));
      --section-help-background: color-mix(in srgb, #f97316 12%, var(--card-background-color));
      --section-help-background-hover: color-mix(in srgb, #f97316 18%, var(--card-background-color));
    }

    .about-workspace .chapter-hero {
      border-color: color-mix(in srgb, #eab308 36%, var(--divider-color));
      --chapter-hero-help-border-color: color-mix(in srgb, #eab308 36%, var(--divider-color));
      --chapter-hero-help-background: color-mix(in srgb, #eab308 15%, var(--card-background-color));
      --chapter-hero-help-background-hover: color-mix(in srgb, #eab308 21%, var(--card-background-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, #eab308 10%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 97%, #fff8de 3%), color-mix(in srgb, var(--secondary-background-color) 92%, #fffaf0 8%));
    }

    .about-workspace .chapter-hero { --chapter-hero-copy-color: color-mix(in srgb, #a16207 88%, white 12%); }
    .about-workspace {
      --section-help-color: color-mix(in srgb, #a16207 88%, white 12%);
      --section-help-border: color-mix(in srgb, #eab308 36%, var(--divider-color));
      --section-help-background: color-mix(in srgb, #eab308 15%, var(--card-background-color));
      --section-help-background-hover: color-mix(in srgb, #eab308 21%, var(--card-background-color));
    }

    .chapter-workspace.collapsed .chapter-hero {
      margin: 0;
    }

    .chapter-hero-inner {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 18px;
      align-items: center;
    }

    .chapter-hero-copy {
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }

    .chapter-hero-title-row {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }

    .chapter-hero-icon {
      display: inline-grid;
      flex: 0 0 auto;
      width: 1.5rem;
      height: 1.5rem;
      place-items: center;
      color: var(--chapter-hero-copy-color);
      filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.42));
    }

    /* Chapter SVGs and the masked Chimes icon share their title's section accent. */
    .chapter-hero-icon :is(svg, .chime-section-icon) {
      color: var(--chapter-hero-copy-color);
    }

    .chapter-hero-icon :is(svg, img) {
      display: block;
      width: 100%;
      height: 100%;
      object-fit: contain;
    }

    .chime-section-icon {
      display: block;
      width: 100%;
      height: 100%;
      background: currentColor;
      -webkit-mask: url("/api/chime_tts/images/option_icons/chime_section.svg") center / contain no-repeat;
      mask: url("/api/chime_tts/images/option_icons/chime_section.svg") center / contain no-repeat;
    }

    .chime-sets-workspace .chapter-hero-icon {
      width: 2.15rem;
      height: 2.15rem;
    }

    .chimes-workspace .chapter-hero-icon {
      width: 2rem;
      height: 2rem;
    }

    .chimes-workspace .chapter-chevron {
      border-color: color-mix(in srgb, var(--primary-color) 26%, var(--divider-color));
      background: color-mix(in srgb, var(--primary-color) 14%, var(--card-background-color));
      color: color-mix(in srgb, var(--primary-color) 42%, black 58%);
    }

    .chapter-hero-title {
      margin: 0;
      font-size: 1.65rem;
      line-height: 1.1;
      letter-spacing: -0.03em;
      color: var(--chapter-hero-copy-color);
    }

    .chapter-hero-description {
      margin: 10px 0 0;  
      font-size: 1rem;
      line-height: 1.6;
      color: var(--chapter-hero-copy-color);
    }

    .chapter-hero-title-row .field-help-link {
      color: var(--chapter-hero-copy-color);
      border-color: var(--chapter-hero-help-border-color);
      background: var(--chapter-hero-help-background);
    }

    .chapter-hero-title-row .field-help-link:hover {
      background: var(--chapter-hero-help-background-hover);
    }

    .chapter-workspace .chapter-content .field-help-link {
      color: var(--section-help-color);
      border-color: var(--section-help-border);
      background: var(--section-help-background);
    }

    .chapter-workspace .chapter-content .field-help-link:hover {
      background: var(--section-help-background-hover);
    }

    .chapter-hero-actions {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
      min-width: 0;
    }

    .chapter-hero-endcap {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 12px;
      min-width: 0;
      align-self: center;
    }

    .chapter-chevron {
      width: 42px;
      height: 42px;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, var(--divider-color) 64%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 84%, white 16%);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: color-mix(in srgb, var(--primary-color) 42%, black 58%);
      flex: 0 0 auto;
    }

    .configuration-workspace .chapter-chevron {
      border-color: color-mix(in srgb, var(--configuration-accent) 30%, var(--divider-color));
      background: color-mix(in srgb, var(--configuration-accent) 16%, var(--card-background-color));
      color: color-mix(in srgb, var(--configuration-accent) 86%, black 14%);
    }

    .notify-workspace .chapter-chevron {
      border-color: color-mix(in srgb, #dc2626 32%, var(--divider-color));
      background: color-mix(in srgb, #dc2626 16%, var(--card-background-color));
      color: color-mix(in srgb, #991b1b 86%, black 14%);
    }

    .logs-workspace .chapter-chevron {
      border-color: color-mix(in srgb, #f97316 34%, var(--divider-color));
      background: color-mix(in srgb, #f97316 18%, var(--card-background-color));
      color: color-mix(in srgb, #9a3412 86%, black 14%);
    }

    .about-workspace .chapter-chevron {
      border-color: color-mix(in srgb, #eab308 38%, var(--divider-color));
      background: color-mix(in srgb, #eab308 20%, var(--card-background-color));
      color: color-mix(in srgb, #854d0e 86%, black 14%);
    }

    @media (prefers-color-scheme: dark) {
      .chime-sets-workspace .chapter-hero {
        border-color: color-mix(in srgb, #8b5cf6 48%, transparent);
      }
      .chime-sets-workspace .chapter-hero { --chapter-hero-copy-color: #a78bfa; }
      .chime-sets-workspace .random-chime-member input[type="checkbox"] { accent-color: #a78bfa; }
      .chime-sets-workspace .chime-sets-chapter-toggle {
        border-color: color-mix(in srgb, #8b5cf6 46%, transparent);
        background: color-mix(in srgb, #7c3aed 10%, var(--card-background-color));
        color: #a78bfa;
      }

      .configuration-workspace .chapter-chevron {
        border-color: color-mix(in srgb, var(--configuration-accent) 46%, transparent);
        background: color-mix(in srgb, var(--configuration-accent) 10%, var(--card-background-color));
        color: color-mix(in srgb, var(--configuration-accent) 82%, white 18%);
      }

      .notify-workspace .chapter-chevron {
        border-color: color-mix(in srgb, #f87171 46%, transparent);
        background: color-mix(in srgb, #dc2626 10%, var(--card-background-color));
        color: color-mix(in srgb, #f87171 78%, white 22%);
      }

      .logs-workspace .chapter-chevron {
        border-color: color-mix(in srgb, #f97316 48%, transparent);
        background: color-mix(in srgb, #f97316 12%, var(--card-background-color));
        color: color-mix(in srgb, #fb923c 86%, white 14%);
      }

      .about-workspace .chapter-chevron {
        border-color: color-mix(in srgb, #eab308 48%, transparent);
        background: color-mix(in srgb, #eab308 14%, var(--card-background-color));
        color: color-mix(in srgb, #facc15 86%, white 14%);
      }
    }

    .chapter-chevron svg {
      width: 20px;
      height: 20px;
      fill: currentColor;
      display: block;
      transform: rotate(-90deg);
      transition: transform 250ms ease;
    }

    .chapter-workspace.expanded .chapter-chevron svg {
      transform: rotate(0deg);
    }

    .chapter-content {
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .chapter-body {
      padding: 2px 0 0;
      background: transparent;
    }

    .chapter-collapse,
    .row-collapse {
      max-height: 0;
      opacity: 0;
      overflow: hidden;
      transition: max-height 250ms ease, opacity 250ms ease;
    }

    .chapter-collapse-inner,
    .row-collapse-inner {
      padding-top: 0;
      transition: padding-top 250ms ease;
    }

    .chapter-collapse.expanded {
      max-height: 5000px;
      opacity: 1;
    }

    .row-collapse.expanded {
      max-height: 4000px;
      opacity: 1;
    }

    .chapter-collapse.expanded .chapter-collapse-inner {
      padding-top: 18px;
    }

    .row-collapse.expanded .row-collapse-inner {
      padding-top: 12px;
    }

    .logs-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .about-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
    }

    .about-footer {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      width: 90px;
    }

    .about-version-line {
      margin: 2px 0 0;
      text-align: center;
      color: var(--secondary-text-color);
      font-size: 0.95rem;
      font-weight: 700;
      letter-spacing: 0.01em;
      inline-size: max-content;
    }

    .about-logo {
      display: block;
      width: 72px;
      height: 72px;
      margin: 18px auto 0;
      object-fit: contain;
      filter: drop-shadow(0 8px 18px rgba(0, 0, 0, 0.18));
    }

    .about-logo-object {
      display: block;
      width: 100%;
      max-width: 650px;
      aspect-ratio: 650 / 520;
      margin: 18px auto 0;
      background: transparent;
      border: 0;
      color-scheme: light dark;
      filter: drop-shadow(0 8px 18px rgba(0, 0, 0, 0.18));
    }

    .about-logo-inline {
      display: block;
      width: 100%;
      max-width: 650px;
      aspect-ratio: 650 / 520;
      margin: 18px auto 0;
      background: transparent;
      border: 0;
      -webkit-tap-highlight-color: transparent;
      user-select: none;
      filter: drop-shadow(0 8px 18px rgba(0, 0, 0, 0.18));
    }

    .about-logo-inline:focus-visible {
      outline: 2px solid color-mix(in srgb, var(--primary-color) 45%, transparent);
      outline-offset: 6px;
      border-radius: 16px;
    }

    .about-logo-inline svg {
      display: block;
      width: 100%;
      height: auto;
      max-width: 650px;
      pointer-events: none;
      background: transparent !important;
      background-color: transparent !important;
      cursor: auto;
    }

    .about-card {
      display: flex;
      flex-direction: column;
      gap: 10px;
      min-height: 100%;
      padding: 16px 18px;
      border-radius: 20px;
      border: 1px solid color-mix(in srgb, #f5c542 34%, var(--divider-color));
      background: color-mix(in srgb, #f5c542 10%, var(--card-background-color) 90%);
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
    }

    .about-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .about-card-title {
      margin: 0;
      font-size: 1rem;
      font-weight: 800;
      color: var(--primary-text-color);
    }

    .about-card-value {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, #f5c542 42%, var(--divider-color));
      background: color-mix(in srgb, #fff5c2 72%, white 28%);
      color: color-mix(in srgb, #7a5b00 88%, black 12%);
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      white-space: nowrap;
    }

    .about-card-description {
      margin: 0;
      color: var(--secondary-text-color);
      line-height: 1.55;
    }

    .about-card-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      align-self: flex-start;
      min-height: 40px;
      padding: 10px 16px;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, #d4a514 36%, transparent);
      background: color-mix(in srgb, #f5c542 18%, transparent);
      color: var(--primary-text-color);
      font-weight: 700;
      text-decoration: none;
      transition: background 150ms ease, border-color 150ms ease;
    }

    .about-card-link:hover {
      background: color-mix(in srgb, #f5c542 26%, transparent);
      border-color: color-mix(in srgb, #d4a514 52%, transparent);
      text-decoration: none;
    }

    .about-card-link:focus-visible {
      outline: 2px solid color-mix(in srgb, #d4a514 55%, transparent);
      outline-offset: 4px;
    }

    .logs-loading {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: var(--secondary-text-color);
      min-height: 44px;
    }

    .logs-loading .button-spinner {
      border-color: color-mix(in srgb, var(--primary-color) 24%, transparent);
      border-top-color: var(--primary-color);
    }

    .logs-list-actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }

    .logs-list-actions-right {
      display: flex;
      justify-content: flex-end;
      margin-left: auto;
    }

    .logs-debug-control {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .logs-debug-control .control-checkbox { display: block; padding: 0; }
    .logs-debug-control .control-checkbox input {
      appearance: none;
      width: 22px;
      height: 22px;
      margin: 0;
      border: 2px solid color-mix(in srgb, #f97316 52%, var(--divider-color));
      border-radius: 7px;
      background: var(--card-background-color);
      cursor: pointer;
    }
    .logs-debug-control .control-checkbox input:checked {
      border-color: #f97316;
      background: #f97316;
    }
    .logs-debug-control .control-checkbox input:checked::after {
      content: "✓";
      display: block;
      color: #fff;
      font-size: 17px;
      font-weight: 800;
      line-height: 18px;
      text-align: center;
    }

    .log-event-row {
      --log-row-accent: color-mix(in srgb, var(--divider-color) 72%, transparent);
      --log-row-accent-solid: var(--primary-color);
      padding: 16px 18px;
      border-radius: 22px;
      border: 2px solid color-mix(in srgb, var(--divider-color) 72%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 82%, transparent);
      cursor: pointer;
    }

    .log-event-row.error {
      --log-row-accent: color-mix(in srgb, var(--error-color, #d32f2f) 56%, transparent);
      --log-row-accent-solid: var(--error-color, #d32f2f);
      border-color: color-mix(in srgb, var(--error-color, #d32f2f) 56%, transparent);
      background: color-mix(in srgb, var(--error-color, #d32f2f) 12%, transparent);
    }

    .log-event-row.warning {
      --log-row-accent: color-mix(in srgb, var(--warning-color, #f59e0b) 56%, transparent);
      --log-row-accent-solid: var(--warning-color, #f59e0b);
      border-color: color-mix(in srgb, var(--warning-color, #f59e0b) 56%, transparent);
      background: color-mix(in srgb, var(--warning-color, #f59e0b) 12%, transparent);
    }

    .log-event-row.initiation {
      --log-row-accent: color-mix(in srgb, #3b82f6 54%, var(--divider-color));
      --log-row-accent-solid: #3b82f6;
      border-color: color-mix(in srgb, #3b82f6 54%, var(--divider-color));
    }

    .log-event-row.configuration {
      --log-row-accent: color-mix(in srgb, #f59e0b 54%, var(--divider-color));
      --log-row-accent-solid: #f59e0b;
      border-color: color-mix(in srgb, #f59e0b 54%, var(--divider-color));
    }

    .log-event-row.action {
      --log-row-accent: color-mix(in srgb, #22c55e 54%, var(--divider-color));
      --log-row-accent-solid: #22c55e;
      border-color: color-mix(in srgb, #22c55e 54%, var(--divider-color));
    }

    .log-event-row.replay {
      --log-row-accent: color-mix(in srgb, #3b82f6 54%, var(--divider-color));
      --log-row-accent-solid: #3b82f6;
      border-color: color-mix(in srgb, #3b82f6 54%, var(--divider-color));
    }

    .log-event-row.clear {
      --log-row-accent: color-mix(in srgb, #a855f7 54%, var(--divider-color));
      --log-row-accent-solid: #a855f7;
      border-color: color-mix(in srgb, #a855f7 54%, var(--divider-color));
    }

    .log-event-row-header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: center;
      min-height: 48px;
    }

    .log-event-row-content {
      min-width: 0;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px 16px;
      justify-content: flex-start;
    }

    .log-event-row-main {
      min-width: 0;
      flex: 1 1 180px;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .log-event-icon {
      width: 28px;
      height: 28px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      background: var(--log-row-accent-solid);
      flex: 0 0 auto;
    }

    .log-event-row.error .log-event-icon {
      background: color-mix(in srgb, var(--error-color, #d32f2f) 72%, black 28%);
      color: #fff;
    }

    .log-event-icon.warning {
      background: color-mix(in srgb, var(--warning-color, #f59e0b) 78%, black 22%);
      color: #fff7ed;
    }

    .log-event-icon.error {
      background: color-mix(in srgb, var(--error-color, #d32f2f) 72%, black 28%);
      color: #fff;
    }

    .log-event-icon svg {
      width: 18px;
      height: 18px;
      fill: currentColor;
      display: block;
    }

    .log-event-copy {
      min-width: 0;
      flex: 1 1 auto;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .log-event-title {
      margin: 0;
      font-size: 1rem;
      font-weight: 700;
      color: var(--primary-text-color);
    }

    .log-event-meta {
      margin: 6px 0 0;
      font-size: 0.88rem;
      color: var(--secondary-text-color);
    }

    .log-event-actions {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: flex-end;
      gap: 8px;
      flex: 0 1 auto;
      margin-left: auto;
      min-width: 0;
    }

    .log-event-row.actions-wrapped .log-event-actions {
      flex: 0 0 100%;
      width: 100%;
      margin-left: 0;
      justify-content: flex-start;
    }

    .log-event-toggle-wrap {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      align-self: center;
    }

    :host([narrow]) .log-event-row-header {
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: start;
    }

    :host([narrow]) .log-event-row-content {
      display: flex;
    }

    :host([narrow]) .log-event-toggle-wrap {
      align-self: start;
    }

    :host([narrow]) .log-event-raw {
      font-size: 0.68rem;
      line-height: 1.4;
    }

    :host([narrow]) .log-event-summary {
      font-size: 0.82rem;
      line-height: 1.45;
    }

    .log-event-row .button-secondary {
      border-color: color-mix(in srgb, var(--log-row-accent-solid) 44%, transparent);
      background: color-mix(in srgb, var(--log-row-accent-solid) 14%, transparent);
      color: var(--primary-text-color);
    }

    .log-event-row .button-secondary:hover,
    .log-event-row .button-secondary:focus-visible {
      border-color: color-mix(in srgb, var(--log-row-accent-solid) 72%, white 28%);
      background: color-mix(in srgb, var(--log-row-accent-solid) 22%, transparent);
    }

    .log-event-toggle {
      min-width: 42px;
      min-height: 42px;
      padding: 0;
    }

    /* Log rows carry their own accent; their chevrons should follow it too. */
    .logs-workspace .log-event-row .log-event-toggle {
      border-color: color-mix(in srgb, var(--log-row-accent-solid) 44%, transparent);
      background: color-mix(in srgb, var(--log-row-accent-solid) 14%, transparent);
      color: var(--primary-text-color);
    }

    .log-event-toggle svg {
      width: 18px;
      height: 18px;
      fill: currentColor;
      display: block;
      transform: rotate(-90deg);
      transition: transform 250ms ease;
    }

    .log-event-toggle.expanded svg {
      transform: rotate(0deg);
    }

    .log-event-body {
      margin-top: 2px;
      padding-top: 14px;
      border-top: 1px solid color-mix(in srgb, var(--divider-color) 66%, transparent);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .copied-label {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }

    .copied-label svg {
      width: 16px;
      height: 16px;
      fill: currentColor;
      display: block;
    }

    .log-event-summary {
      margin: 0;
      color: var(--secondary-text-color);
      line-height: 1.6;
      word-break: break-word;
    }

    .log-event-raw {
      margin: 0;
      padding: 14px 16px;
      border-radius: 18px;
      border: 1px solid color-mix(in srgb, var(--divider-color) 70%, transparent);
      background: color-mix(in srgb, var(--secondary-background-color) 92%, black 8%);
      color: var(--primary-text-color);
      font-size: 0.84rem;
      line-height: 1.5;
      overflow-x: auto;
      overflow-y: hidden;
      white-space: pre;
    }

    .log-event-raw-line {
      display: block;
      width: max-content;
      min-width: 100%;
      padding: 1px 6px;
      margin: 0 -6px;
      border-radius: 8px;
    }

    .log-event-raw-line.warning {
      color: color-mix(in srgb, var(--warning-color, #f59e0b) 82%, var(--primary-text-color) 18%);
      background: color-mix(in srgb, var(--warning-color, #f59e0b) 16%, transparent);
      font-weight: 700;
    }

    .log-event-raw-line.error {
      color: color-mix(in srgb, var(--error-color, #d32f2f) 84%, var(--primary-text-color) 16%);
      background: color-mix(in srgb, var(--error-color, #d32f2f) 14%, transparent);
      font-weight: 700;
    }

    .section {
      padding: 22px;
    }

    .chapter-hero .section {
      border-radius: 24px;
      border: 1px solid color-mix(in srgb, var(--divider-color) 72%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 84%, transparent);
    }

    .configuration-workspace .chapter-hero .section {
      border-color: color-mix(in srgb, var(--configuration-accent) 32%, var(--divider-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--configuration-accent) 12%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 92%, white 8%), color-mix(in srgb, var(--secondary-background-color) 84%, transparent));
      box-shadow: none;
    }

    .notify-workspace .chapter-hero .section {
      background: color-mix(in srgb, var(--card-background-color) 76%, black 24%);
      border-color: color-mix(in srgb, #dc2626 18%, var(--divider-color));
    }

    .notify-workspace .chapter-body,
    .logs-workspace .chapter-body {
      background: transparent;
    }

    .section-header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: center;
    }

    .config-section-card {
      cursor: pointer;
    }

    .config-section-card.collapsed .section-header {
      margin-bottom: 0;
    }

    .section-header-copy {
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }

    .section-header-actions {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      flex: 0 0 auto;
    }

    .section-header-copy-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .section-header h2 {
      margin: 0 0 6px;
      font-size: 1.25rem;
      letter-spacing: -0.02em;
    }

    .config-section-toggle {
      min-width: 42px;
      min-height: 42px;
      padding: 0;
      flex: 0 0 auto;
      background: color-mix(in srgb, var(--primary-color) 12%, var(--divider-color));
    }

    .config-section-toggle svg {
      width: 18px;
      height: 18px;
      fill: currentColor;
      display: block;
      transform: rotate(-90deg);
      transition: transform 250ms ease;
    }

    .config-section-toggle.expanded svg {
      transform: rotate(0deg);
    }

    .config-section-body {
      margin-top: 2px;
      padding-top: 14px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .chime-sets-workspace .config-section-body {
      padding-top: 0;
    }

    .chimes-workspace .chapter-hero :is(.section, .config-section, .field) {
      border-color: color-mix(in srgb, var(--primary-color) 32%, var(--divider-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--primary-color) 12%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 94%, white 6%), color-mix(in srgb, var(--secondary-background-color) 78%, transparent));
      box-shadow: none;
    }

    .chimes-workspace .chime-list-section {
      container-type: inline-size;
      container-name: chime-list;
      /* The list expands after its toggle animation begins. On mobile, scroll
       * anchoring can otherwise pull the viewport back to this header once
       * that layout shift completes. */
      overflow-anchor: none;
    }

    /* A long, single-column list changes the document height substantially on
     * narrow screens. Do not animate that change while a touch scroll may be
     * in progress, otherwise mobile browsers can clamp the page back to this
     * section when the animation ends. */
    .chime-list-section > .row-collapse,
    .chime-list-section > .row-collapse > .row-collapse-inner {
      transition: none;
    }

    .chimes-workspace .chime-list-grid {
      display: block;
      column-count: 1;
      column-gap: 0;
      margin-top: 14px;
      background: none;
    }

    .chimes-workspace .chime-list-grid .random-chime-member {
      break-inside: avoid-column;
    }

    @container chime-list (min-width: 700px) {
      .chimes-workspace .chime-list-grid {
        column-count: 2;
        background: linear-gradient(to right, transparent calc(50% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(50% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(50% + 0.5px), transparent calc(50% + 0.5px));
      }
    }

    @container chime-list (min-width: 1120px) {
      .chimes-workspace .chime-list-grid {
        column-count: 3;
        background:
          linear-gradient(to right, transparent calc(33.333% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(33.333% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(33.333% + 0.5px), transparent calc(33.333% + 0.5px)),
          linear-gradient(to right, transparent calc(66.667% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(66.667% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(66.667% + 0.5px), transparent calc(66.667% + 0.5px));
      }
    }

    @media (min-width: 560px) {
      .chimes-workspace .chime-list-grid {
        column-count: 2;
        background: linear-gradient(to right, transparent calc(50% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(50% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(50% + 0.5px), transparent calc(50% + 0.5px));
      }
    }

    @media (min-width: 920px) {
      .chimes-workspace .chime-list-grid {
        column-count: 3;
        background:
          linear-gradient(to right, transparent calc(33.333% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(33.333% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(33.333% + 0.5px), transparent calc(33.333% + 0.5px)),
          linear-gradient(to right, transparent calc(66.667% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(66.667% - 0.5px), color-mix(in srgb, var(--primary-color) 42%, var(--divider-color)) calc(66.667% + 0.5px), transparent calc(66.667% + 0.5px));
      }
    }

    .chimes-workspace .chime-list-member > span {
      min-width: 0;
      overflow: visible;
      overflow-wrap: anywhere;
      text-overflow: clip;
      white-space: normal;
    }

    .chimes-workspace .chime-list-member .field-preview-button {
      margin-left: auto;
    }

    .chimes-workspace .chime-list-member {
      padding-right: 16px;
      padding-left: 16px;
    }

    .chime-sets-workspace .random-chime-set-card {
      container-type: inline-size;
    }

    .chime-sets-workspace .chime-set-member-grid {
      display: block;
      column-count: 1;
      column-gap: 0;
      background: none;
    }

    .chime-sets-workspace .chime-set-member-grid .random-chime-member {
      break-inside: avoid-column;
    }

    .chime-sets-workspace .chime-set-member-grid .random-chime-member {
      padding-right: 16px;
      padding-left: 16px;
    }

    .chime-sets-workspace .chime-set-member-grid label {
      flex: 1 1 auto;
      min-width: 0;
    }

    .chime-sets-workspace .chime-set-member-grid label span {
      overflow: visible;
      overflow-wrap: anywhere;
      text-overflow: clip;
      white-space: normal;
    }

    .chime-sets-workspace .chime-set-member-grid .field-preview-button {
      margin-left: auto;
    }

    @media (min-width: 560px) {
      .chime-sets-workspace .chime-set-member-grid {
        column-count: 2;
        background: linear-gradient(to right, transparent calc(50% - 0.5px), color-mix(in srgb, #7c3aed 42%, var(--divider-color)) calc(50% - 0.5px), color-mix(in srgb, #7c3aed 42%, var(--divider-color)) calc(50% + 0.5px), transparent calc(50% + 0.5px));
      }
    }

    @media (min-width: 920px) {
      .chime-sets-workspace .chime-set-member-grid {
        column-count: 3;
        background:
          linear-gradient(to right, transparent calc(33.333% - 0.5px), color-mix(in srgb, #7c3aed 42%, var(--divider-color)) calc(33.333% - 0.5px), color-mix(in srgb, #7c3aed 42%, var(--divider-color)) calc(33.333% + 0.5px), transparent calc(33.333% + 0.5px)),
          linear-gradient(to right, transparent calc(66.667% - 0.5px), color-mix(in srgb, #7c3aed 42%, var(--divider-color)) calc(66.667% - 0.5px), color-mix(in srgb, #7c3aed 42%, var(--divider-color)) calc(66.667% + 0.5px), transparent calc(66.667% + 0.5px));
      }
    }

    .random-chime-sets-card { cursor: pointer; }
    .random-chime-set-row-toggle {
      display: flex;
      flex: 1 1 auto;
      min-width: 0;
      align-items: center;
      border: 0;
      padding: 0;
      background: transparent;
      color: inherit;
      text-align: left;
      font: inherit;
      cursor: pointer;
    }

    .random-chime-set-card.expanded .random-chime-set-row-toggle {
      display: none;
    }

    .random-chime-set-card [data-delete-random-chime-set] {
      width: 42px;
      min-width: 42px;
      min-height: 42px;
      padding: 0;
      border-radius: 999px;
    }
    .random-chime-member-grid {
      display: grid;
      grid-auto-flow: column;
      grid-auto-columns: minmax(0, 1fr);
      gap: 8px 16px;
    }
    .random-chime-member {
      display: flex;
      align-items: center;
      gap: 9px;
      min-width: 0;
      padding: 8px 0;
      font-size: .9rem;
    }
    .random-chime-member label { display: flex; align-items: center; gap: 9px; min-width: 0; }
    .random-chime-member span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .random-chime-member .field-preview-button {
      width: 30px;
      min-width: 30px;
      min-height: 30px;
      padding: 0;
      flex: 0 0 auto;
      border-radius: 999px;
    }
    .random-chime-member .chime-set-offset-button {
      width: 30px;
      min-width: 30px;
      min-height: 30px;
      padding: 0;
      flex: 0 0 auto;
      border-radius: 999px;
    }
    .chime-set-offset-control {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    [data-chime-set-offset-reset]:disabled {
      border-color: var(--divider-color);
      color: var(--divider-color);
    }
    .chime-set-offset-dialog .confirm-actions > :is([data-chime-set-offset-reset], [data-chime-set-offset-close]) {
      width: 112px;
    }
    .chime-set-offset-value {
      appearance: none;
      padding: 0;
      border: 0;
      border-bottom: 1px dashed currentColor;
      background: transparent;
      color: inherit;
      cursor: pointer;
      font: inherit;
      font-variant-numeric: tabular-nums;
    }
    .chime-set-offset-value:focus-visible {
      outline: 2px solid color-mix(in srgb, var(--primary-color) 55%, transparent);
      outline-offset: 3px;
    }
    .chime-set-offset-title-input {
      width: 8ch;
      min-width: 8ch;
      padding: 2px 4px;
      border: 1px solid var(--accent-color, var(--primary-color));
      border-radius: 6px;
      background: transparent;
      color: inherit;
      font: inherit;
      font-variant-numeric: tabular-nums;
      text-align: center;
    }
    .chime-set-offset-control .field-label { flex: 0 0 auto; }
    .chime-set-offset-input.control {
      width: 14ch;
      min-width: 14ch;
      text-align: center;
      font-variant-numeric: tabular-nums;
    }
    .chime-set-offset-timeline {
      position: relative;
      height: 140px;
      overflow: hidden;
      border: 1px solid color-mix(in srgb, var(--divider-color) 80%, transparent);
      border-radius: 16px;
      background: color-mix(in srgb, var(--card-background-color) 72%, var(--primary-color) 4%);
      touch-action: none;
      user-select: none;
    }
    .chime-set-offset-axis {
      position: relative;
      height: 14px;
      margin-bottom: 2px;
      color: var(--secondary-text-color);
      font-size: .72rem;
      font-variant-numeric: tabular-nums;
      line-height: 1;
    }
    .chime-set-offset-axis-label {
      position: absolute;
      top: 0;
      transform: translateX(-50%);
      white-space: nowrap;
    }
    .chime-set-offset-grid-line {
      position: absolute;
      z-index: 0;
      top: 0;
      bottom: 0;
      width: 1px;
      background: color-mix(in srgb, var(--primary-text-color) 14%, transparent);
      pointer-events: none;
    }
    .chime-set-offset-timeline::after {
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: linear-gradient(90deg, transparent, color-mix(in srgb, var(--primary-text-color) 5%, transparent), transparent);
    }
    .chime-set-offset-audio {
      position: absolute;
      height: 34px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-sizing: border-box;
      padding: 8px 12px;
      border: 1px solid currentColor;
      border-radius: 10px;
      cursor: ew-resize;
      opacity: .68;
      transition: left 80ms linear, width 80ms linear;
      outline-offset: 3px;
    }
    .chime-set-offset-timeline.dragging :is(.chime-set-offset-audio, .chime-set-offset-overlap-line) {
      transition: none;
    }
    .chime-set-offset-timeline.initializing :is(.chime-set-offset-audio, .chime-set-offset-overlap-line, .chime-set-offset-playback-head) {
      visibility: hidden;
    }
    .chime-set-offset-tts { top: 76px; }
    .chime-set-offset-waveform { top: 30px; }
    .chime-set-offset-audio:focus-visible {
      outline: 2px solid var(--primary-color);
    }
    .chime-set-offset-waveform {
      z-index: 2;
      padding-right: 0;
      padding-left: 0;
      color: var(--primary-color);
      background: color-mix(in srgb, var(--primary-color) 35%, transparent);
    }
    .chime-set-offset-waveform svg {
      width: 100%;
      min-width: 0;
      height: 22px;
      pointer-events: none;
    }
    .chime-set-offset-waveform .chime-set-offset-audio-label {
      top: -15px;
      bottom: auto;
    }
    .chime-set-offset-tts {
      z-index: 1;
      color: var(--accent-color, #ff9800);
      background: color-mix(in srgb, var(--accent-color, #ff9800) 38%, transparent);
    }
    .chime-set-offset-audio-label {
      position: absolute;
      bottom: -23px;
      left: 50%;
      max-width: 100%;
      overflow: hidden;
      color: var(--secondary-text-color);
      font-size: .72rem;
      font-weight: 600;
      line-height: 1;
      text-overflow: ellipsis;
      text-transform: uppercase;
      white-space: nowrap;
      transform: translateX(-50%);
      pointer-events: none;
    }
    .chime-set-offset-tts .chime-set-offset-audio-label {
      top: 50%;
      bottom: auto;
      transform: translate(-50%, -50%);
    }
    .chime-set-offset-overlap-line {
      position: absolute;
      z-index: 3;
      top: 30px;
      height: 74px;
      width: 2px;
      display: none;
      background: var(--error-color, #d32f2f);
      box-shadow: 0 0 0 1px color-mix(in srgb, var(--error-color, #d32f2f) 25%, transparent);
      transition: left 80ms linear;
      pointer-events: none;
    }
    .chime-set-offset-playback-head {
      position: absolute;
      z-index: 4;
      top: 0;
      bottom: 0;
      left: 0;
      width: 2px;
      display: none;
      background: #000;
      pointer-events: none;
    }
    .chime-set-offset-playback-head.playing {
      display: block;
      animation: chimeSetOffsetPlayback var(--chime-set-preview-duration, 1s) linear forwards;
    }
    @keyframes chimeSetOffsetPlayback { to { left: calc(100% - 2px); } }
    .chime-set-offset-title-hint {
      margin: 0px;
      color: var(--secondary-text-color);
      font-size: .95rem;
      line-height: 1.4;
      text-align: center;
    }
    .chime-set-offset-hint-row {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      margin-top: 0;
    }
    .chime-set-offset-preview-button {
      width: 108px;
      min-width: 108px;
      min-height: 30px;
      padding: 0 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      border-color: var(--success-color, #2e7d32);
      color: var(--success-color, #2e7d32);
    }
    .chime-set-offset-preview-button.stop {
      border-color: var(--error-color, #d32f2f);
      color: var(--error-color, #d32f2f);
    }
    .chime-set-offset-preview-button svg { width: 18px; height: 18px; }
    .chime-set-offset-timeline-status {
      color: var(--primary-text-color);
      font-variant-numeric: tabular-nums;
    }
    .random-chime-member input[type="checkbox"] {
      width: 22px;
      height: 22px;
      flex: 0 0 auto;
    }
    .chime-sets-workspace .random-chime-member input[type="checkbox"] {
      accent-color: #7c3aed;
    }
    .random-chime-set-title-input {
      width: 100%;
      min-width: 0;
      padding: 4px 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      box-shadow: none;
    }
    .random-chime-set-title-input:focus { box-shadow: none; }

    /* Keep the editable set name and its two actions in one responsive row. */
    .random-chime-set-card .notify-profile-header {
      flex-wrap: nowrap;
    }

    .random-chime-set-card .notify-profile-copy,
    .random-chime-set-card .notify-profile-title-edit {
      flex: 1 1 0;
      min-width: 0;
    }

    .random-chime-set-card .notify-profile-title-edit {
      width: auto;
    }

    :host([narrow]) .random-chime-member-grid:not(.chime-list-grid):not(.chime-set-member-grid) {
      grid-template-rows: none !important;
      grid-auto-flow: row;
      grid-template-columns: 1fr;
    }
    :host([narrow]) .chimes-workspace .chime-list-member {
      padding-right: 16px;
      padding-left: 16px;
    }
    :host([narrow]) .random-chime-member .field-preview-button { margin-left: auto; }

    .field-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }

    :host([narrow]) .field-grid {
      grid-template-columns: 1fr;
    }

    .field {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 16px;
      border-radius: 18px;
      background: color-mix(in srgb, var(--secondary-background-color) 64%, transparent);
      border: 1px solid transparent;
    }

    .configuration-workspace .field {
      border: 1px solid color-mix(in srgb, var(--configuration-accent) 32%, var(--divider-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--configuration-accent) 12%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 92%, white 8%), color-mix(in srgb, var(--secondary-background-color) 84%, transparent));
      box-shadow: none;
    }

    .field.wide {
      grid-column: 1 / -1;
    }

    .field.error {
      border-color: rgba(211, 47, 47, 0.45);
      background: rgba(211, 47, 47, 0.05);
    }

    .field.error .control,
    .field.error .control-select {
      border-color: color-mix(in srgb, var(--error-color, #d32f2f) 68%, var(--divider-color));
      box-shadow: 0 0 0 1px color-mix(in srgb, var(--error-color, #d32f2f) 22%, transparent);
    }

    .field.changed {
      border-color: color-mix(in srgb, var(--primary-color) 38%, transparent);
      background: color-mix(in srgb, var(--primary-color) 7%, transparent);
    }

    .field-top {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      column-gap: 12px;
      row-gap: 0px;
      align-items: start;
    }

    .field-header {
      display: flex;
      gap: 14px;
      align-items: flex-start;
      min-width: 0;
    }

    .field-top.with-icon {
      grid-template-columns: 56px minmax(0, 1fr) auto;
    }

    .field-top.with-icon .field-icon {
      grid-column: 1;
      grid-row: 1 / span 2;
      align-self: center;
    }

    .field-top.with-icon .field-header {
      grid-column: 2;
      grid-row: 1;
      align-self: start;
    }

    .field-top.with-icon .required {
      grid-column: 3;
      grid-row: 1;
      align-self: start;
    }

    .field-top.with-icon .field-description-row {
      grid-column: 2 / 4;
      grid-row: 2;
      align-self: start;
    }

    .field-icon {
      width: 56px;
      height: 56px;
      flex: 0 0 56px;
      display: block;
      object-fit: cover;
      filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.42));
    }

    @media (prefers-color-scheme: light) {
      :is(.field-icon, .chapter-hero-icon) {
        filter: drop-shadow(0 2px 6px rgba(15, 23, 42, 0.22));
      }
    }

    .field-copy {
      min-width: 0;
    }

    .field-description-row {
      grid-column: 1 / -1;
      min-width: 0;
      align-self: start;
    }

    .field-label {
      margin: 0;
      font-weight: 700;
      color: var(--primary-text-color);
    }

    .field-changed-pill {
      padding: 2px 8px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--primary-color) 14%, transparent);
      color: var(--primary-color);
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }

    .field-label-row {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: nowrap;
      min-width: 0;
    }

    .field-label-row > .field-label {
      min-width: 0;
      flex: 0 1 auto;
    }

    .field-label-row > .field-help-link,
    .field-label-row > .field-changed-pill,
    .field-label-row > .field-reset-link {
      flex: 0 0 auto;
    }

    .field-label-row .spacer {
      flex: 1 1 auto;
    }

    .field-reset-link {
      appearance: none;
      padding: 0;
      border: 0;
      background: transparent;
      color: var(--primary-color);
      font: inherit;
      font-size: 0.84rem;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      white-space: nowrap;
    }

    .field-reset-link:hover {
      text-decoration: underline;
    }

    .field-reset-link:focus-visible {
      outline: 2px solid color-mix(in srgb, var(--primary-color) 45%, transparent);
      outline-offset: 2px;
    }

    .field-help-link {
      width: 22px;
      height: 22px;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, var(--primary-color) 34%, transparent);
      color: var(--primary-color);
      background: color-mix(in srgb, var(--primary-color) 10%, transparent);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      font-size: 0.82rem;
      font-weight: 700;
      line-height: 1;
      flex: 0 0 auto;
    }

    .field-help-link:hover {
      background: color-mix(in srgb, var(--primary-color) 16%, transparent);
      text-decoration: none;
    }

    .field-help-link:focus-visible {
      outline: 2px solid color-mix(in srgb, var(--primary-color) 45%, transparent);
      outline-offset: 2px;
    }

    .field-description {
      margin: 0;
      font-size: 0.92rem;
      color: var(--secondary-text-color);
    }

    .required {
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--primary-color);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      white-space: nowrap;
    }

    .control,
    .control-select {
      width: 100%;
      border: 1px solid var(--divider-color);
      border-radius: 14px;
      background: var(--card-background-color);
      color: var(--primary-text-color);
      padding: 12px 14px;
      font: inherit;
    }

    .control-select {
      appearance: none;
      padding-right: 46px;
      background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%23b8c7d1%27 stroke-width=%272.2%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpath d=%27M7 10l5 5 5-5%27/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: calc(100% - 15px) center;
      background-size: 18px 18px;
    }

    .control:focus,
    .control-select:focus {
      outline: 2px solid color-mix(in srgb, var(--primary-color) 45%, transparent);
      outline-offset: 0;
      border-color: var(--primary-color);
    }

    .input-row {
      display: flex;
      gap: 10px;
      align-items: stretch;
    }

    .input-row .control {
      flex: 1 1 auto;
      min-width: 0;
    }

    .input-row .control-select {
      flex: 1 1 auto;
      min-width: 0;
    }

    .field-preview-button {
      flex: 0 0 auto;
      align-self: stretch;
    }

    .preview-playing {
      position: relative;
      isolation: isolate;
      overflow: hidden;
      background: #16a34a !important;
      border-color: #22c55e !important;
    }

    .preview-playing::before {
      content: "";
      position: absolute;
      inset: 0;
      z-index: 0;
      background: color-mix(in srgb, var(--secondary-background-color) 92%, var(--card-background-color));
      clip-path: circle(0% at 50% 50%);
      animation: previewRadialWipe var(--preview-duration, 1s) linear forwards;
    }

    .preview-playing > svg,
    .preview-playing > span { position: relative; z-index: 1; }

    @keyframes previewRadialWipe {
      to { clip-path: circle(75% at 50% 50%); }
    }

    @media (prefers-reduced-motion: reduce) {
      .preview-playing::before { animation: none; clip-path: circle(75% at 50% 50%); }
    }

    .browse-button {
      flex: 0 0 auto;
      padding: 12px 16px;
      border-radius: 14px;
      border: 1px solid var(--divider-color);
      // background: color-mix(in srgb, var(--card-background-color) 92%, white 8%);
      color: var(--primary-text-color);
      box-shadow: none;
    }

    .configuration-workspace .field .browse-button {
      border-color: color-mix(in srgb, var(--configuration-accent) 12%, var(--divider-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--configuration-accent) 14%, transparent), transparent 42%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 92%, white 8%), color-mix(in srgb, var(--secondary-background-color) 84%, transparent));
      color: var(--primary-text-color);
      box-shadow: none;
    }

    .configuration-workspace .field .browse-button:hover,
    .configuration-workspace .field .browse-button:focus-visible {
      border-color: color-mix(in srgb, var(--configuration-accent) 22%, var(--divider-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--configuration-accent) 18%, transparent), transparent 42%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 94%, white 6%), color-mix(in srgb, var(--secondary-background-color) 86%, transparent));
    }

    .browse-button:disabled {
      opacity: 0.7;
    }

    .path-inline-action {
      flex: 0 0 auto;
      padding: 10px 14px;
      min-height: 48px;
      border-radius: 14px;
      border: 1px solid color-mix(in srgb, var(--error-color, #d32f2f) 42%, transparent);
      background: color-mix(in srgb, var(--error-color, #d32f2f) 12%, transparent);
      color: var(--primary-text-color);
      box-shadow: none;
      white-space: nowrap;
    }

    .control-checkbox {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 4px 0;
      font-weight: 600;
      color: var(--primary-text-color);
    }

    .control-checkbox input {
      width: 20px;
      height: 20px;
      accent-color: var(--primary-color);
    }

    .error-text {
      font-size: 0.84rem;
      color: var(--error-color, #d32f2f);
    }

    .error-text:empty {
      display: none;
    }

    .field-note {
      padding: 12px 14px;
      border-radius: 14px;
      font-size: 0.88rem;
      line-height: 1.45;
      border: 1px solid color-mix(in srgb, var(--primary-color) 24%, transparent);
      background: color-mix(in srgb, var(--primary-color) 10%, transparent);
      color: var(--primary-text-color);
    }

    .field-subhint {
      padding: 10px 12px;
      border-radius: 14px;
      font-size: 0.86rem;
      line-height: 1.45;
      border: 1px solid var(--divider-color);
      background: color-mix(in srgb, var(--secondary-background-color) 64%, transparent);
      color: var(--secondary-text-color);
    }

    .field-subhint.info {
      border-color: color-mix(in srgb, var(--primary-color) 24%, transparent);
      background: color-mix(in srgb, var(--primary-color) 10%, transparent);
      color: var(--primary-text-color);
    }

    .field-subhint.success {
      border-color: color-mix(in srgb, var(--success-color, #2e7d32) 26%, transparent);
      background: color-mix(in srgb, var(--success-color, #2e7d32) 10%, transparent);
      color: var(--primary-text-color);
    }

    .field-subhint.error {
      border-color: color-mix(in srgb, var(--error-color, #d32f2f) 26%, transparent);
      background: color-mix(in srgb, var(--error-color, #d32f2f) 8%, transparent);
      color: var(--primary-text-color);
    }

    .field-subhint-links {
      margin-top: 8px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .field-subhint-links a {
      color: var(--primary-color);
      text-decoration: none;
      font-weight: 600;
      word-break: break-all;
    }

    .field-subhint-links a:hover {
      text-decoration: underline;
    }

    .footer {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      padding: 0px 2px 8px;
    }

    .loading {
      min-height: calc(100vh - 160px);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 56px 24px;
    }

    .loading-spinner {
      width: 42px;
      height: 42px;
      border: 4px solid color-mix(in srgb, var(--primary-color, #03a9f4) 20%, transparent);
      border-top-color: var(--primary-color, #03a9f4);
      border-radius: 50%;
      animation: buttonSpin 0.8s linear infinite;
    }

    .error-recovery {
      min-height: calc(100vh - 220px);
      padding: 200px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .error-recovery .button-primary {
      min-width: 140px;
    }

    .picker-modal-backdrop {
      position: fixed;
      top: var(--modal-top, 0px);
      left: var(--modal-left, 0px);
      width: var(--modal-width, 100vw);
      height: var(--modal-height, 100vh);
      z-index: 1200;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      background: rgba(9, 14, 20, 0.56);
      backdrop-filter: blur(10px);
    }

    .picker-loading-overlay {
      position: absolute;
      inset: 0;
      z-index: 1;
      display: grid;
      place-items: center;
      background: color-mix(in srgb, var(--card-background-color) 12%, transparent);
      pointer-events: all;
    }

    .picker-modal {
      position: relative;
      width: min(980px, calc(100vw - 32px));
      height: min(86vh, 820px);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border-radius: 20px;
      border: 1px solid color-mix(in srgb, var(--divider-color) 82%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 98%, black 2%);
      box-shadow: 0 28px 68px rgba(0, 0, 0, 0.34);
    }

    .picker-modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-height: 60px;
      padding: 12px 14px;
      border-bottom: 1px solid color-mix(in srgb, var(--divider-color) 82%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 96%, white 4%);
    }

    .picker-modal-title {
      margin: 0;
      min-width: 0;
      color: var(--primary-text-color);
      font-size: 1rem;
      font-weight: 700;
      line-height: 1.35;
    }

    .picker-modal-close {
      min-width: 38px;
      min-height: 38px;
      width: 38px;
      height: 38px;
      padding: 0;
      border-radius: 999px;
      border-color: color-mix(in srgb, var(--divider-color) 82%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 88%, white 12%);
      flex: 0 0 38px;
    }

    .picker-dialog-body {
      min-height: 0;
      display: flex;
      flex: 1 1 auto;
      flex-direction: column;
      gap: 0;
      overflow: hidden;
      background: color-mix(in srgb, var(--card-background-color) 98%, black 2%);
    }

    .picker-error-banner {
      margin: 15px;
    }

    .picker-dialog-footer {
      margin-top: 0;
      padding: 12px 14px;
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: 12px;
      flex-wrap: nowrap;
      border-top: 1px solid color-mix(in srgb, var(--divider-color) 82%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 96%, white 4%);
    }

    .picker-dialog-footer .button-secondary,
    .picker-dialog-footer .button-primary {
      min-width: 132px;
      min-height: 40px;
      border-radius: 10px;
    }

    .picker-dialog-lead {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .picker-dialog-lead p {
      margin: 0;
      color: var(--secondary-text-color);
      line-height: 1.5;
    }

    .confirm-overlay {
      position: fixed;
      top: var(--modal-top, 0px);
      left: var(--modal-left, 0px);
      width: var(--modal-width, 100vw);
      height: var(--modal-height, 100vh);
      z-index: 40;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: rgba(0, 0, 0, 0.45);
      backdrop-filter: blur(6px);
    }

    .confirm-dialog {
      width: min(520px, 100%);
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 22px;
      border-radius: 24px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color);
      box-shadow: 0 20px 48px rgba(0, 0, 0, 0.28);
    }

    .confirm-title {
      margin: 0;
      color: var(--primary-text-color);
      font-size: 1.2rem;
      font-weight: 700;
      text-align: center;
    }

    .confirm-copy {
      margin: 0;
      color: var(--secondary-text-color);
      line-height: 1.6;
      text-align: center;
    }

    .confirm-actions {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .picker-empty {
      margin: 0;
      color: var(--secondary-text-color);
      line-height: 1.5;
    }

    .picker-location-label {
      margin: 0 0 8px;
      color: var(--secondary-text-color);
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    .advanced-toggle-row {
      display: flex;
      justify-content: flex-start;
      margin-top: 16px;
    }

    .advanced-toggle {
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid var(--divider-color);
      background: transparent;
      color: var(--primary-text-color);
      box-shadow: none;
    }

    .advanced-fields {
      margin-top: 16px;
    }

    .picker-preview {
      padding: 10px 12px;
      border-top: 1px solid color-mix(in srgb, var(--divider-color) 72%, transparent);
      background: color-mix(in srgb, var(--secondary-background-color) 52%, transparent);
    }

    .picker-preview-title {
      margin: 0 0 6px;
      color: var(--primary-text-color);
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .picker-preview-title.centered {
      margin-bottom: 0;
      text-align: center;
    }

    .picker-preview-list {
      margin: 0;
      padding-left: 16px;
      color: var(--secondary-text-color);
      line-height: 1.45;
      font-size: 0.9rem;
    }

    .picker-browser-shell {
      display: grid;
      grid-template-columns: 240px minmax(0, 1fr);
      gap: 0;
      flex: 1 1 auto;
      height: 100%;
      min-height: 560px;
      background: color-mix(in srgb, var(--card-background-color) 98%, black 2%);
    }

    .picker-browser-sidebar {
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 14px;
      border-right: 1px solid color-mix(in srgb, var(--divider-color) 82%, transparent);
      background: color-mix(in srgb, var(--secondary-background-color) 72%, var(--card-background-color) 28%);
    }

    .picker-sidebar-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 2px 2px 0;
    }

    .picker-sidebar-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 0;
    }

    .picker-root {
      width: 100%;
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid transparent;
      background: transparent;
      color: inherit;
      text-align: left;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
      gap: 2px;
      cursor: pointer;
      transition: background 140ms ease, border-color 140ms ease;
    }

    .picker-root:hover,
    .picker-root:focus-visible {
      text-decoration: none;
      border-color: color-mix(in srgb, var(--divider-color) 82%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 78%, transparent);
    }

    .picker-root.active {
      text-decoration: none;
      border-color: color-mix(in srgb, var(--primary-color) 26%, var(--divider-color));
      background: color-mix(in srgb, var(--primary-color) 11%, var(--card-background-color) 89%);
    }

    .picker-root-title {
      color: var(--primary-text-color);
      font-size: 0.93rem;
      font-weight: 700;
      line-height: 1.35;
    }

    .picker-root-path {
      display: block;
      min-width: 0;
      overflow: hidden;
      color: var(--secondary-text-color);
      font-size: 0.76rem;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      line-height: 1.35;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .picker-browser-main {
      display: flex;
      flex: 1 1 auto;
      flex-direction: column;
      min-width: 0;
      min-height: 0;
      background: color-mix(in srgb, var(--card-background-color) 97%, black 3%);
    }

    .picker-browser-toolbar {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      gap: 10px;
      min-width: 0;
      padding: 12px 14px;
      border-bottom: 1px solid color-mix(in srgb, var(--divider-color) 82%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 96%, white 4%);
    }

    .picker-browser-toolbar-left,
    .picker-browser-toolbar-right {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }

    .picker-browser-toolbar-left {
      min-width: 0;
    }

    .picker-browser-toolbar-right {
      justify-self: end;
      position: relative;
    }

    .picker-toolbar-button {
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }

    .picker-toolbar-button svg,
    .picker-file-kind svg,
    .picker-breadcrumb-home svg {
      width: 16px;
      height: 16px;
      fill: currentColor;
      display: block;
    }

    .picker-search {
      width: 100%;
      min-width: 0;
      min-height: 40px;
      border-radius: 10px;
      border-color: color-mix(in srgb, var(--divider-color) 86%, transparent);
      background: color-mix(in srgb, var(--secondary-background-color) 46%, var(--card-background-color) 54%);
      box-shadow: none;
    }

    .picker-pathbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-width: 0;
      padding: 10px 14px;
      border-bottom: 1px solid color-mix(in srgb, var(--divider-color) 74%, transparent);
      background: color-mix(in srgb, var(--secondary-background-color) 36%, transparent);
    }

    .picker-pathbar-main {
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .picker-pathbar-label {
      margin: 0;
      color: var(--secondary-text-color);
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .picker-breadcrumbs {
      display: flex;
      align-items: center;
      gap: 3px;
      flex-wrap: wrap;
      min-width: 0;
    }

    .picker-breadcrumb-home {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      margin-right: 7px;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, var(--divider-color) 78%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 84%, white 16%);
      color: var(--secondary-text-color);
      box-shadow: none;
      padding: 0;
    }

    .picker-path-button {
      min-height: 28px;
      padding: 3px 6px;
      border-radius: 10px;
      border: 1px solid color-mix(in srgb, var(--primary-color) 16%, transparent);
      background: color-mix(in srgb, var(--primary-color) 7%, transparent);
      color: var(--primary-text-color);
      box-shadow: none;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.84rem;
      font-weight: 600;
    }

    .picker-path-button:hover,
    .picker-path-button:focus-visible {
      background: color-mix(in srgb, var(--primary-color) 10%, transparent);
      border-color: color-mix(in srgb, var(--primary-color) 20%, transparent);
    }

    .picker-path-separator {
      color: var(--secondary-text-color);
      font-size: 0.8rem;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }

    .picker-filebrowser-table-wrap {
      min-width: 0;
      flex: 1 1 auto;
      min-height: 0;
      overflow: auto;
      background: color-mix(in srgb, var(--card-background-color) 99%, black 1%);
    }

    .picker-filebrowser-table-wrap.empty {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .picker-filebrowser-table-wrap.has-empty-message {
      position: relative;
    }

    .picker-empty {
      margin: 0;
      padding: 18px 14px;
      color: var(--secondary-text-color);
      font-size: 0.92rem;
      text-align: center;
    }

    .picker-empty.picker-empty-overlay {
      position: absolute;
      inset: 50% 14px auto;
      transform: translateY(-50%);
      pointer-events: none;
    }

    .picker-filebrowser-table {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }

    .picker-file-row {
      display: grid;
      grid-template-columns: minmax(0, 1.7fr) minmax(110px, 0.72fr) minmax(74px, 0.46fr) auto;
      gap: 12px;
      align-items: center;
      padding: 11px 14px;
      min-width: 0;
      border-top: 1px solid color-mix(in srgb, var(--divider-color) 68%, transparent);
      transition: background 140ms ease, box-shadow 140ms ease;
    }

    .picker-file-row:first-child {
      border-top: 0;
    }

    .picker-file-row.selected {
      background: color-mix(in srgb, var(--primary-color) 12%, transparent);
      box-shadow: inset 2px 0 0 color-mix(in srgb, var(--primary-color) 74%, transparent);
    }

    .picker-file-row.parent {
      background: color-mix(in srgb, var(--secondary-background-color) 46%, transparent);
      color: inherit;
      text-align: left;
      cursor: pointer;
    }

    .picker-file-row.folder:hover,
    .picker-file-row.folder:focus-within,
    .picker-file-row.parent:hover,
    .picker-file-row.parent:focus-within {
      background: color-mix(in srgb, var(--primary-color) 7%, transparent);
    }

    .picker-file-name {
      min-width: 0;
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 600;
      color: var(--primary-text-color);
      line-height: 1.35;
    }

    .picker-file-kind {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex: 0 0 auto;
      color: color-mix(in srgb, var(--primary-color) 72%, var(--secondary-text-color));
    }

    .picker-file-kind.audio svg {
      width: 20px;
      height: 20px;
    }

    .picker-file-open {
      padding: 0;
      border: 0;
      background: transparent;
      color: inherit;
      box-shadow: none;
      font: inherit;
      font-weight: inherit;
      text-align: left;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      cursor: pointer;
      border-radius: 0;
    }

    .picker-file-open:hover,
    .picker-file-open:focus-visible {
      text-decoration: underline;
    }

    .picker-file-meta,
    .picker-file-size {
      color: var(--secondary-text-color);
      font-size: 0.84rem;
      min-width: 0;
      white-space: nowrap;
    }

    .picker-file-size {
      text-align: right;
    }

    .picker-file-actions {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 6px;
    }

    .picker-overflow-toggle {
      min-width: 38px;
      min-height: 38px;
      border-radius: 10px;
      border-color: color-mix(in srgb, var(--divider-color) 82%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 88%, white 12%);
    }

    .picker-overflow-toggle svg {
      width: 18px;
      height: 18px;
      fill: currentColor;
      display: block;
    }

    .picker-overflow-menu {
      position: absolute;
      top: calc(100% + 8px);
      right: 0;
      z-index: 4;
      min-width: 177px;
      padding: 6px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      border-radius: 12px;
      border: 1px solid color-mix(in srgb, var(--divider-color) 86%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 98%, black 2%);
      box-shadow: 0 16px 32px rgba(0, 0, 0, 0.22);
    }

    .picker-overflow-item {
      width: 100%;
      min-height: 38px;
      gap: 15px;
      justify-content: flex-start;
      text-align: left;
      border-radius: 8px;
      box-shadow: none;
      border-color: transparent;
      background: transparent;
    }

    .picker-overflow-item svg {
      width: 16px;
      height: 16px;
      flex: 0 0 auto;
      display: block;
      overflow: visible;
    }

    .picker-overflow-item:hover,
    .picker-overflow-item:focus-visible {
      background: color-mix(in srgb, var(--primary-color) 10%, transparent);
      border-color: color-mix(in srgb, var(--primary-color) 18%, transparent);
    }

    .picker-file-row {
      cursor: pointer;
    }

    .picker-file-row-main {
      display: grid;
      grid-template-columns: minmax(0, 1.7fr) minmax(110px, 0.72fr) minmax(74px, 0.46fr);
      grid-column: 1 / 4;
      gap: 12px;
      min-width: 0;
      min-height: 38px;
      align-items: center;
      grid-auto-flow: column;
    }

    .picker-file-row:focus-visible .picker-file-name-text,
    .picker-file-row:hover .picker-file-name-text {
      text-decoration: underline;
    }

    .picker-file-name-text {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .picker-file-actions .icon-only-button {
      min-width: 38px;
      min-height: 38px;
    }

    .picker-action-overlay {
      position: absolute;
      inset: 0;
      z-index: 45;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: rgba(5, 9, 18, 0.5);
      backdrop-filter: blur(8px);
    }

    .picker-action-dialog {
      position: relative;
      width: min(460px, 100%);
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 22px;
      border-radius: 24px;
      border: 1px solid color-mix(in srgb, var(--divider-color) 85%, transparent);
      background: color-mix(in srgb, var(--card-background-color) 96%, black 4%);
      box-shadow: 0 24px 54px rgba(0, 0, 0, 0.32);
    }

    .picker-action-header {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .picker-action-header-bar {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      gap: 12px;
    }

    .picker-action-close {
      position: absolute;
      top: 16px;
      right: 16px;
      min-width: 38px;
      min-height: 38px;
      border-radius: 999px;
      flex: 0 0 auto;
    }

    .picker-action-dialog.conflicts .picker-action-header-bar {
      display: block;
    }

    .picker-action-title {
      margin: 0;
      color: var(--primary-text-color);
      font-size: 1.05rem;
      font-weight: 700;
    }

    .picker-action-copy {
      margin: 0;
      color: var(--secondary-text-color);
      line-height: 1.55;
      text-align: center;
    }

    .picker-action-form {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .picker-action-field {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .picker-action-field label {
      color: var(--secondary-text-color);
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }

    .picker-action-actions {
      display: flex;
      justify-content: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .picker-action-dialog.conflicts .picker-action-header,
    .picker-action-dialog.conflicts .picker-action-form,
    .picker-action-dialog.conflicts .picker-action-actions {
      align-items: center;
      text-align: center;
    }

    .picker-action-dialog.conflicts .picker-action-actions {
      justify-content: center;
    }

    .picker-action-dialog.upload-folder .picker-action-header,
    .picker-action-dialog.upload-folder .picker-action-form,
    .picker-action-dialog.upload-folder .picker-action-actions {
      align-items: center;
      text-align: center;
    }

    .picker-action-dialog.upload-folder .picker-action-actions {
      justify-content: center;
    }

    .notify-profile-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .notify-profile-list-actions {
      display: flex;
      justify-content: flex-start;
      gap: 8px;
      margin-bottom: 2px;
    }

    .notify-workspace .notify-profile-list-actions,
    .chime-sets-workspace .notify-profile-list-actions {
      padding-inline: 14px;
    }

    .notify-profile-list-actions .button-primary {
      box-shadow: none;
    }

    .notify-profile-list-actions > :is(.button-primary, .button-secondary) {
      box-sizing: border-box;
      height: 44px;
    }

    .notify-profile-card {
      padding: 14px 16px;
      border-radius: 20px;
      border: 1px solid var(--divider-color);
      background: color-mix(in srgb, var(--secondary-background-color) 58%, transparent);
    }

    .chime-sets-workspace .random-chime-set-card {
      border-color: color-mix(in srgb, #7c3aed 32%, var(--divider-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, #7c3aed 16%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 97%, #f5f1ff 3%), color-mix(in srgb, var(--secondary-background-color) 92%, #f8f5ff 8%));
    }

    .notify-workspace .notify-profile-card {
      border-color: color-mix(in srgb, #dc2626 28%, var(--divider-color));
      background:
        radial-gradient(circle at top right, color-mix(in srgb, #dc2626 12%, transparent), transparent 44%),
        linear-gradient(180deg, color-mix(in srgb, var(--card-background-color) 97%, #fff4f5 3%), color-mix(in srgb, var(--secondary-background-color) 92%, #fff7f8 8%));
    }

    .notify-profile-card.error {
      border-color: color-mix(in srgb, var(--error-color, #d32f2f) 62%, var(--divider-color));
      box-shadow: 0 0 0 1px color-mix(in srgb, var(--error-color, #d32f2f) 18%, transparent);
    }

    .notify-profile-validation-error {
      width: 100%;
      margin: -2px 0 2px;
      color: #ff0000;
      font-size: 0.86rem;
      font-weight: 600;
      line-height: 1.4;
    }

    .notify-profile-validation-error.validation-flash {
      animation: validationErrorFlash 170ms ease-in-out 3;
    }

    @keyframes validationErrorFlash {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.2;
      }
    }

    .notify-profile-title-input.error {
      border: 1px solid color-mix(in srgb, var(--error-color, #d32f2f) 68%, var(--divider-color));
      border-radius: 10px;
      box-shadow: 0 0 0 1px color-mix(in srgb, var(--error-color, #d32f2f) 22%, transparent);
    }

    .notify-profile-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      min-height: 48px;
    }

    .notify-profile-card.collapsed .notify-profile-header {
      min-height: 48px;
      flex-wrap: nowrap;
    }

    .notify-profile-copy h3 {
      margin: 0;
      font-size: 1.02rem;
    }

    .notify-profile-title-display {
      padding-left: 15px;
    }

    .random-chime-set-title-name {
      font-weight: 700;
    }

    .random-chime-set-title-count {
      color: var(--secondary-text-color);
      font-weight: 400;
    }

    .notify-profile-title-display,
    .notify-profile-title-edit {
      min-width: 0;
      flex: 1 1 auto;
    }

    .notify-profile-title-edit {
      display: none;
    }

    .notify-profile-card.expanded .notify-profile-title-display {
      display: none;
    }

    .notify-profile-card.expanded .notify-profile-title-edit {
      display: block;
    }

    .notify-profile-copy p {
      margin: 0;
    }

    .notify-profile-copy {
      min-width: 0;
      display: flex;
      align-items: center;
      min-height: 40px;
      flex: 1 1 auto;
      overflow: hidden;
    }

    .notify-profile-card.collapsed .notify-profile-copy h3 {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .notify-profile-copy.testing {
      display: none;
    }

    .notify-profile-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: nowrap;
      flex: 0 1 auto;
      min-width: 0;
    }

    .notify-profile-actions:not(.testing) {
      margin-left: auto;
      flex: 0 0 auto;
    }

    .notify-profile-actions button {
      min-height: 40px;
      padding: 10px 16px;
      flex: 0 0 auto;
      white-space: nowrap;
    }

    .notify-profile-actions [data-toggle-notify-profile],
    .notify-profile-actions [data-toggle-random-chime-set] {
      width: 42px;
      min-width: 42px;
      min-height: 42px;
      padding: 0;
      border-radius: 999px;
    }

    .config-section-toggle,
    .log-event-toggle,
    .notify-profile-actions [data-toggle-notify-profile],
    .notify-profile-actions [data-toggle-random-chime-set] {
      width: 42px;
      min-width: 42px;
      height: 42px;
      min-height: 42px;
      padding: 0;
      border: 1px solid color-mix(in srgb, var(--divider-color) 64%, transparent);
      border-radius: 999px;
      background: color-mix(in srgb, var(--card-background-color) 84%, white 16%);
      color: color-mix(in srgb, var(--primary-color) 42%, black 58%);
      box-shadow: none;
    }

    .config-section-toggle svg,
    .log-event-toggle svg,
    .notify-profile-actions [data-toggle-notify-profile] svg,
    .notify-profile-actions [data-toggle-random-chime-set] svg {
      width: 20px;
      height: 20px;
    }

    .configuration-workspace .config-section-toggle {
      border-color: color-mix(in srgb, var(--configuration-accent) 30%, var(--divider-color));
      background: color-mix(in srgb, var(--configuration-accent) 16%, var(--card-background-color));
      color: color-mix(in srgb, var(--configuration-accent) 86%, black 14%);
    }

    .configuration-workspace .chapter-content { --workspace-accent: color-mix(in srgb, var(--configuration-accent) 82%, white 18%); }
    .chime-sets-workspace .chapter-content { --workspace-accent: #7c3aed; }
    .chimes-workspace .chapter-content { --workspace-accent: var(--primary-color); }
    .notify-workspace .chapter-content { --workspace-accent: #b91c1c; }

    :is(.configuration-workspace, .chime-sets-workspace, .chimes-workspace, .notify-workspace) .chapter-content :is(
      .section-header h2,
      .section-header p,
      .field-label,
      .field-description,
      .required,
      .hint,
      .notify-profile-copy h3,
      .notify-profile-copy p,
      .random-chime-member,
      .random-chime-set-title-count
    ) {
      color: var(--workspace-accent);
    }

    :is(.configuration-workspace, .chime-sets-workspace, .chimes-workspace, .notify-workspace) .chapter-content :is(.button-secondary, .advanced-toggle):not([data-open-notify-test]) {
      color: var(--workspace-accent);
    }

    :is(.configuration-workspace, .chime-sets-workspace, .chimes-workspace, .notify-workspace) .chapter-content .field-preview-button {
      border-color: color-mix(in srgb, var(--workspace-accent) 46%, var(--divider-color));
      background: color-mix(in srgb, var(--workspace-accent) 14%, var(--card-background-color));
      color: var(--workspace-accent);
    }

    :is(.configuration-workspace, .chime-sets-workspace, .chimes-workspace, .notify-workspace) .chapter-content .field-preview-button:hover,
    :is(.configuration-workspace, .chime-sets-workspace, .chimes-workspace, .notify-workspace) .chapter-content .field-preview-button:focus-visible {
      border-color: color-mix(in srgb, var(--workspace-accent) 68%, var(--divider-color));
      background: color-mix(in srgb, var(--workspace-accent) 22%, var(--card-background-color));
    }

    :is(.configuration-workspace, .chime-sets-workspace, .chimes-workspace, .notify-workspace) .chapter-content .field-preview-button.preview-playing {
      background: var(--workspace-accent) !important;
      border-color: color-mix(in srgb, var(--workspace-accent) 72%, white 28%) !important;
      color: var(--card-background-color);
    }

    :is(.configuration-workspace, .chime-sets-workspace, .chimes-workspace, .notify-workspace) .chapter-content .field-preview-button.preview-playing::before {
      background: color-mix(in srgb, var(--workspace-accent) 14%, var(--card-background-color));
    }

    .logs-workspace .logs-list-actions > a.button-secondary {
      border-color: color-mix(in srgb, #f97316 34%, var(--divider-color));
      background: color-mix(in srgb, #f97316 18%, var(--card-background-color));
      color: color-mix(in srgb, #f97316 86%, white 14%);
    }

    .chime-sets-workspace .notify-profile-list-actions .button-primary {
      border-color: color-mix(in srgb, #7c3aed 34%, var(--divider-color));
      background: color-mix(in srgb, #7c3aed 18%, var(--card-background-color));
      color: color-mix(in srgb, #5b21b6 82%, white 18%);
    }

    .notify-workspace .notify-profile-list-actions .button-primary {
      border-color: color-mix(in srgb, #dc2626 34%, var(--divider-color));
      background: color-mix(in srgb, #dc2626 18%, var(--card-background-color));
      color: color-mix(in srgb, #dc2626 82%, white 18%);
    }

    .chime-sets-workspace :is(.config-section-toggle, .log-event-toggle) {
      border-color: color-mix(in srgb, #7c3aed 30%, var(--divider-color));
      background: color-mix(in srgb, #7c3aed 16%, var(--card-background-color));
      color: color-mix(in srgb, #5b21b6 82%, black 18%);
    }

    .chimes-workspace :is(.config-section-toggle, .log-event-toggle) {
      border-color: color-mix(in srgb, var(--primary-color) 26%, var(--divider-color));
      background: color-mix(in srgb, var(--primary-color) 14%, var(--card-background-color));
      color: color-mix(in srgb, var(--primary-color) 42%, black 58%);
    }

    .notify-workspace :is(.log-event-toggle, .notify-profile-actions [data-toggle-notify-profile]) {
      border-color: color-mix(in srgb, #dc2626 32%, var(--divider-color));
      background: color-mix(in srgb, #dc2626 16%, var(--card-background-color));
      color: color-mix(in srgb, #991b1b 86%, black 14%);
    }

    .notify-workspace .notify-profile-actions :is([data-open-notify-test], [data-run-notify-inline-test]:not(:disabled)) {
      color: #fff;
      background: linear-gradient(135deg, #dc2626, #991b1b);
      border-color: #991b1b;
      box-shadow: 0 12px 22px rgba(220, 38, 38, 0.24);
    }

    .notify-workspace .notify-profile-actions :is([data-open-notify-test], [data-run-notify-inline-test]:not(:disabled)):hover,
    .notify-workspace .notify-profile-actions :is([data-open-notify-test], [data-run-notify-inline-test]:not(:disabled)):focus-visible {
      background: linear-gradient(135deg, #ef4444, #991b1b);
      border-color: #7f1d1d;
    }

    .notify-workspace .notify-entity-chip {
      border-color: color-mix(in srgb, #dc2626 34%, var(--divider-color));
      background: color-mix(in srgb, #dc2626 14%, var(--card-background-color));
      color: color-mix(in srgb, #991b1b 86%, black 14%);
    }

    .notify-workspace .notify-target-picker {
      --primary-color: var(--workspace-accent);
      --mdc-theme-primary: var(--workspace-accent);
      --ha-color-fill-primary-normal-resting: var(--workspace-accent);
      --ha-color-fill-primary-loud-resting: var(--workspace-accent);
      --wa-color-fill-normal: var(--workspace-accent);
      --wa-color-fill-loud: var(--workspace-accent);
      --wa-color-brand-fill-normal: var(--workspace-accent);
      --wa-color-brand-fill-loud: var(--workspace-accent);
      --wa-color-on-normal: #fff;
      --button-color-fill-normal-hover: #dc2626;
      --button-color-fill-normal-active: #991b1b;
      --button-color-fill-loud-hover: #dc2626;
      --button-color-fill-loud-active: #991b1b;
    }

    .logs-workspace .log-event-toggle {
      border-color: color-mix(in srgb, #f97316 34%, var(--divider-color));
      background: color-mix(in srgb, #f97316 18%, var(--card-background-color));
      color: color-mix(in srgb, #9a3412 86%, black 14%);
    }

    @media (prefers-color-scheme: dark) {
      .configuration-workspace .config-section-toggle {
        border-color: color-mix(in srgb, var(--configuration-accent) 46%, transparent);
        background: color-mix(in srgb, var(--configuration-accent) 10%, var(--card-background-color));
        color: color-mix(in srgb, var(--configuration-accent) 82%, white 18%);
      }

      .chime-sets-workspace .chapter-content { --workspace-accent: #a78bfa; }
      .chimes-workspace .chapter-content { --workspace-accent: var(--primary-color); }
      .notify-workspace .chapter-content { --workspace-accent: #f87171; }

      .chime-sets-workspace .notify-profile-list-actions .button-primary {
        border-color: color-mix(in srgb, #7c3aed 48%, transparent);
        background: color-mix(in srgb, #7c3aed 12%, var(--card-background-color));
        color: color-mix(in srgb, #7c3aed 82%, white 18%);
      }

      .notify-workspace .notify-profile-list-actions .button-primary {
        border-color: color-mix(in srgb, #dc2626 48%, transparent);
        background: color-mix(in srgb, #dc2626 12%, var(--card-background-color));
        color: color-mix(in srgb, #dc2626 82%, white 18%);
      }

      .logs-workspace .logs-list-actions > a.button-secondary {
        border-color: color-mix(in srgb, #f97316 48%, transparent);
        background: color-mix(in srgb, #f97316 12%, var(--card-background-color));
        color: color-mix(in srgb, #f97316 86%, white 14%);
      }

      .chime-sets-workspace :is(.config-section-toggle, .log-event-toggle) {
        border-color: color-mix(in srgb, #8b5cf6 46%, transparent);
        background: color-mix(in srgb, #7c3aed 10%, var(--card-background-color));
        color: #a78bfa;
      }

      .chimes-workspace .chapter-hero { --chapter-hero-copy-color: color-mix(in srgb, var(--primary-color) 78%, white 22%); }

      .chimes-workspace .chapter-chevron {
        border-color: color-mix(in srgb, var(--primary-color) 42%, transparent);
        background: color-mix(in srgb, var(--primary-color) 10%, var(--card-background-color));
        color: color-mix(in srgb, var(--primary-color) 78%, white 22%);
      }

      .chimes-workspace .chapter-hero :is(.section, .config-section) { border-color: color-mix(in srgb, var(--primary-color) 38%, transparent); }


      .chimes-workspace :is(.config-section-toggle, .log-event-toggle) {
        border-color: color-mix(in srgb, var(--primary-color) 42%, transparent);
        background: color-mix(in srgb, var(--primary-color) 10%, var(--card-background-color));
        color: color-mix(in srgb, var(--primary-color) 78%, white 22%);
      }

      .notify-workspace :is(.log-event-toggle, .notify-profile-actions [data-toggle-notify-profile]) {
        border-color: color-mix(in srgb, #f87171 46%, transparent);
        background: color-mix(in srgb, #dc2626 10%, var(--card-background-color));
        color: color-mix(in srgb, #f87171 78%, white 22%);
      }

      .notify-workspace .notify-entity-chip {
        border-color: color-mix(in srgb, #f87171 46%, transparent);
        background: color-mix(in srgb, #dc2626 10%, var(--card-background-color));
        color: color-mix(in srgb, #f87171 78%, white 22%);
      }

      .logs-workspace .log-event-toggle {
        border-color: color-mix(in srgb, #f97316 48%, transparent);
        background: color-mix(in srgb, #f97316 12%, var(--card-background-color));
        color: color-mix(in srgb, #fb923c 86%, white 14%);
      }
    }

    .notify-profile-actions [data-open-notify-test] {
      min-width: 42px;
      min-height: 42px;
      padding: 0 14px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      color: #ecfdf5;
      background: linear-gradient(180deg, rgba(21, 128, 61, 0.5), rgba(20, 83, 45, 0.42));
      border-color: rgba(22, 101, 52, 0.72);
    }

    .notify-profile-actions [data-open-notify-test]:hover,
    .notify-profile-actions [data-open-notify-test]:focus-visible {
      background: linear-gradient(180deg, rgba(22, 163, 74, 0.6), rgba(20, 83, 45, 0.55));
      border-color: rgba(34, 197, 94, 0.78);
    }

    .notify-profile-actions [data-open-notify-test] svg {
      width: 20px;
      height: 20px;
      display: block;
      fill: currentColor;
    }

    @media (prefers-color-scheme: light) {
      .notify-profile-actions [data-open-notify-test] {
        color: #ffffff;
        background: linear-gradient(180deg, #15803d, #166534);
        border-color: #14532d;
        box-shadow:
          inset 0 1px 0 rgba(255, 255, 255, 0.72),
          0 0 0 1px rgba(22, 163, 74, 0.14);
      }

      .notify-profile-actions [data-open-notify-test]:hover,
      .notify-profile-actions [data-open-notify-test]:focus-visible {
        background: linear-gradient(180deg, #16a34a, #14532d);
        border-color: #14532d;
      }

      .notify-profile-actions [data-open-notify-test] svg {
        filter: drop-shadow(0 1px 0 rgba(255, 255, 255, 0.45));
      }
    }

    .notify-profile-actions [data-run-notify-inline-test]:disabled {
      border: 1px solid color-mix(in srgb, var(--divider-color) 82%, var(--primary-text-color) 18%);
    }

    /* Keep every notification-profile action visually aligned with Add Profile. */
    .notify-workspace .notify-profile-actions :is(
      [data-open-notify-test],
      [data-run-notify-inline-test],
      [data-close-notify-test]
    ) {
      border-color: color-mix(in srgb, #dc2626 34%, var(--divider-color));
      background: color-mix(in srgb, #dc2626 18%, var(--card-background-color));
      color: color-mix(in srgb, #dc2626 82%, white 18%);
      box-shadow: none;
    }

    .notify-workspace .notify-profile-actions :is(
      [data-open-notify-test],
      [data-run-notify-inline-test]:not(:disabled),
      [data-close-notify-test]
    ):hover,
    .notify-workspace .notify-profile-actions :is(
      [data-open-notify-test],
      [data-run-notify-inline-test]:not(:disabled),
      [data-close-notify-test]
    ):focus-visible {
      color: #fff;
    }

    @media (prefers-color-scheme: dark) {
      .notify-workspace .notify-profile-actions :is(
        [data-open-notify-test],
        [data-run-notify-inline-test],
        [data-close-notify-test]
      ) {
        border-color: color-mix(in srgb, #dc2626 48%, transparent);
        background: color-mix(in srgb, #dc2626 12%, var(--card-background-color));
        color: color-mix(in srgb, #dc2626 82%, white 18%);
      }
    }

    .notify-profile-actions [data-remove-notify-profile] {
      width: 42px;
      min-width: 42px;
      min-height: 42px;
      padding: 0;
      border-radius: 999px;
    }

    .notify-profile-actions.testing {
      flex: 1 1 auto;
      width: 100%;
      justify-content: stretch;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto auto;
      align-items: center;
    }

    .notify-inline-test-input {
      min-width: 0;
      width: 100%;
    }

    .notify-inline-test-sent {
      width: auto;
      padding: 0 14px;
      white-space: nowrap;
    }

    .button-danger {
      color: #fff;
      background: color-mix(in srgb, var(--error-color, #d32f2f) 80%, black 20%);
      border: 1px solid color-mix(in srgb, var(--error-color, #d32f2f) 72%, white 28%);
      box-shadow: none;
    }

    .icon-only-button {
      min-width: 40px;
      padding: 0;
    }

    .select-preview-row .icon-only-button {
      width: 40px;
      min-width: 40px;
      min-height: 40px;
      border-radius: 50%;
    }

    .icon-only-button svg {
      width: 18px;
      height: 18px;
      fill: currentColor;
      display: block;
    }

    .notify-profile-title-input {
      width: min(100%, 320px);
      min-height: 44px;
      padding: 10px 14px;
      border-radius: 14px;
      border: 1px solid var(--divider-color);
      background: color-mix(in srgb, var(--card-background-color) 90%, white 10%);
      color: var(--primary-text-color);
      font: inherit;
      font-size: 1.02rem;
      font-weight: 700;
    }

    .notify-profile-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 12px;
      margin-top: 12px;
    }

    .notify-profile-grid.compact .field,
    .notify-profile-flags .field {
      gap: 4px;
      padding: 10px 12px;
      border-radius: 14px;
      background: transparent;
      border-color: var(--accent-color, var(--primary-color));
    }

    /* Keep every notification-profile field on the same surface as its section header. */
    .notify-workspace .notify-profile-card .field {
      background: var(--notify-section-surface);
    }

    /* Every field follows its workspace accent; validation errors retain red. */
    .chapter-workspace .field:not(.error) {
      border-color: var(--section-help-border);
    }

    .chapter-workspace .field:not(.error) input[type="range"] {
      accent-color: var(--section-help-color);
    }

    .chapter-workspace .control-checkbox {
      color: var(--section-help-color);
    }

    .chapter-workspace .control-checkbox input {
      accent-color: var(--section-help-color);
    }

    .notify-profile-flags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px 12px;
      margin-top: 8px;
      justify-content: flex-start;
      align-items: flex-start;
    }

    .notify-profile-flags .field {
      flex: 1 1 180px;
      min-width: 160px;
    }

    .notify-flag-checkbox {
      justify-content: flex-start;
      min-height: 40px;
    }

    .notify-entity-chip-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .notify-entity-chip {
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, var(--primary-color) 28%, transparent);
      background: color-mix(in srgb, var(--primary-color) 10%, transparent);
      color: var(--primary-text-color);
      box-shadow: none;
      font-weight: 600;
    }

    .notify-entity-picker {
      display: block;
      margin-top: 6px;
    }

    .notify-section-header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      gap: 16px;
    }

    .notify-section-copy {
      min-width: 0;
    }

    .notify-section-title-row {
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }

    .notify-section-title-row h2 {
      margin: 0;
    }

    .notify-section-actions {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 10px;
      width: max-content;
      justify-self: end;
    }

    .notify-test-panel {
      margin-bottom: 16px;
      padding: 16px;
      border-radius: 18px;
      border: 1px solid var(--divider-color);
      background: color-mix(in srgb, var(--card-background-color) 90%, white 10%);
    }

    .notify-test-panel-header h3 {
      margin: 0;
      font-size: 1.05rem;
    }

    .notify-test-panel-header {
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      align-items: center;
      gap: 12px;
    }

    .notify-test-panel-title {
      grid-column: 2;
      min-width: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      text-align: center;
    }

    .notify-test-panel-title p {
      margin-top: 6px;
    }

    .notify-test-panel-actions {
      grid-column: 3;
      display: flex;
      align-items: center;
      gap: 8px;
      margin-left: auto;
      justify-self: end;
    }

    .icon-button {
      min-width: 40px;
      min-height: 40px;
      padding: 0;
      border-radius: 999px;
      border: 1px solid var(--divider-color);
      background: color-mix(in srgb, var(--card-background-color) 88%, white 12%);
      color: var(--primary-text-color);
      box-shadow: none;
      font-size: 1.1rem;
      line-height: 1;
    }

    .icon-button-chevron {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: transform 150ms ease;
    }

    .icon-button-chevron.expanded {
      transform: rotate(180deg);
    }

    .notify-range {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 110px;
      align-items: center;
      gap: 10px;
    }

    .notify-range-number {
      width: 100%;
      min-width: 0;
      text-align: right;
    }

    .control-range {
      width: 100%;
      margin: 0;
    }

    .control-range::-webkit-slider-runnable-track {
      min-height: 6px;
      border-radius: 999px;
      background: linear-gradient(
        to right,
        color-mix(in srgb, var(--section-help-color) 84%, black 16%) 0 var(--range-progress, 0%),
        var(--card-background-color) var(--range-progress, 0%) 100%
      );
    }

    .control-range::-moz-range-track {
      min-height: 6px;
      border-radius: 999px;
      background: var(--card-background-color);
    }

    .control-range::-moz-range-progress {
      min-height: 6px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--section-help-color) 84%, black 16%);
    }

    .notify-test-grid {
      display: grid;
      grid-template-columns: 220px minmax(0, 1fr);
      gap: 12px;
      margin-top: 12px;
    }

    .notify-test-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 12px;
    }

    .control-textarea {
      min-height: 110px;
      resize: vertical;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }

    .script-action-label {
      margin: 14px 0 6px;
      color: color-mix(in srgb, var(--section-help-color) 88%, var(--primary-text-color));
      font-size: 0.82rem;
      font-weight: 700;
    }

    .script-action-label:first-of-type { margin-top: 0; }

    @media (max-width: 1100px) {
      .field-grid {
        grid-template-columns: 1fr;
      }

      .notify-profile-grid {
        grid-template-columns: 1fr;
      }

      .notify-test-grid {
        grid-template-columns: 1fr;
      }

      .notify-test-panel-header {
        grid-template-columns: 1fr;
      }

      .notify-test-panel-title,
      .notify-test-panel-actions {
        grid-column: auto;
      }

      .notify-test-panel-actions {
        justify-self: end;
      }
    }

    @media (max-width: 720px) {
      .notify-section-header {
        grid-template-columns: 1fr;
      }

      .notify-section-actions {
        align-items: flex-start;
        justify-self: start;
      }
    }

    :host([narrow]) .topbar-nav {
      display: inline-flex;
    }

    :host([narrow]) .layout {
      padding:
        16px
        calc(16px + var(--panel-safe-area-right))
        calc(16px + var(--panel-safe-area-bottom))
        calc(16px + var(--panel-safe-area-left));
    }

    :host([narrow]) .topbar {
      height: 56px;
      padding:
        0
        calc(16px + var(--panel-safe-area-right))
        0
        calc(16px + var(--panel-safe-area-left));
      gap: 12px;
    }

    :host([narrow]) .topbar-notice {
      padding:
        0
        calc(16px + var(--panel-safe-area-right))
        12px
        calc(16px + var(--panel-safe-area-left));
    }

    :host([narrow]) .transient-banner {
      right: calc(16px + var(--panel-safe-area-right));
      left: calc(16px + var(--panel-safe-area-left));
    }

    :host([narrow]) .section {
      border-radius: 20px;
      padding: 18px;
    }

    :host([narrow]) .chapter-hero {
      padding: 18px;
      border-radius: 22px;
    }

    :host([narrow]) .chapter-hero-title {
      font-size: 1.4rem;
    }

    :host([narrow]) .topbar-actions {
      gap: 8px;
    }

    :host([narrow]) .topbar-link {
      display: none;
    }

    :host([narrow]) .input-row {
      flex-direction: column;
    }

    :host([narrow]) .input-row.select-preview-row {
      flex-direction: row;
    }

    :host([narrow]) .picker-modal-backdrop {
      padding:
        calc(8px + var(--panel-safe-area-top))
        calc(8px + var(--panel-safe-area-right))
        calc(8px + var(--panel-safe-area-bottom))
        calc(8px + var(--panel-safe-area-left));
    }

    :host([narrow]) .picker-modal {
      width: calc(100vw - 16px - var(--panel-safe-area-left) - var(--panel-safe-area-right));
      height: calc(100vh - 16px - var(--panel-safe-area-top) - var(--panel-safe-area-bottom));
      max-width: calc(100vw - 16px - var(--panel-safe-area-left) - var(--panel-safe-area-right));
      max-height: calc(100vh - 16px - var(--panel-safe-area-top) - var(--panel-safe-area-bottom));
      border-radius: 16px;
    }

    :host([narrow]) .picker-browser-shell {
      grid-template-columns: minmax(0, 1fr);
      grid-template-rows: 87px minmax(0, 1fr);
      min-height: 0;
      flex: 1 1 auto;
    }

    :host([narrow]) .picker-browser-sidebar {
      box-sizing: border-box;
      display: flex;
      flex-direction: row;
      align-items: stretch;
      height: 87px;
      min-height: 87px;
      max-height: 87px;
      gap: 8px;
      overflow: hidden;
      padding: 12px 14px;
      border-right: 0;
      border-bottom: 1px solid color-mix(in srgb, var(--divider-color) 82%, transparent);
    }

    :host([narrow]) .picker-sidebar-header {
      flex: 0 0 auto;
      align-items: flex-start;
      padding-top: 9px;
    }

    :host([narrow]) .picker-location-label {
      margin: 0;
    }

    :host([narrow]) .picker-sidebar-list {
      align-self: flex-start;
      flex: 1 1 auto;
      flex-direction: row;
      align-items: flex-start;
      height: 62px;
      min-height: 62px;
      max-height: 62px;
      overflow-x: auto;
      padding-bottom: 2px;
    }

    :host([narrow]) .picker-sidebar-list .picker-root {
      box-sizing: border-box;
      flex: 0 0 auto;
      width: fit-content;
      max-width: min(70vw, 240px);
      min-height: 60px;
    }

    :host([narrow]) .picker-sidebar-list .picker-root-path {
      max-width: min(56vw, 200px);
    }

    :host([narrow]) .picker-root {
      align-items: flex-start;
      text-align: left;
    }

    :host([narrow]) .picker-browser-toolbar {
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
    }

    :host([narrow]) .picker-pathbar {
      align-items: flex-start;
      flex-direction: column;
    }

    :host([narrow]) .picker-file-row,
    :host([narrow]) .picker-file-row.parent {
      grid-template-columns: minmax(0, 1fr) auto;
    }

    :host([narrow]) .picker-file-row .picker-file-meta,
    :host([narrow]) .picker-file-row .picker-file-size,
    :host([narrow]) .picker-file-row.parent .picker-file-meta,
    :host([narrow]) .picker-file-row.parent .picker-file-size {
      display: none;
    }

    :host([narrow]) .picker-file-row-main {
      grid-template-columns: minmax(0, 1fr);
      grid-column: 1 / 2;
    }

    @media (max-width: 600px) {
      .layout {
        padding:
          16px
          calc(16px + var(--panel-safe-area-right))
          calc(16px + var(--panel-safe-area-bottom))
          calc(16px + var(--panel-safe-area-left));
      }

      .topbar {
        height: 56px;
        padding:
          0
          calc(16px + var(--panel-safe-area-right))
          0
          calc(16px + var(--panel-safe-area-left));
      }

      .transient-banner {
        right: calc(16px + var(--panel-safe-area-right));
        left: calc(16px + var(--panel-safe-area-left));
      }

      .topbar-notice {
        padding:
          0
          calc(16px + var(--panel-safe-area-right))
          12px
          calc(16px + var(--panel-safe-area-left));
      }

      .section {
        border-radius: 20px;
      }

      .section {
        padding: 18px;
      }

      .notify-profile-header {
        align-items: stretch;
      }

      .picker-dialog-footer {
        justify-content: space-between;
      }

      .picker-dialog-footer .button-secondary,
      .picker-dialog-footer .button-primary {
        flex: 0 1 auto;
      }
    }
  </style>
  <div class="snowfall" id="snowfall" aria-hidden="true"></div>
  <div class="topbar-wrap" id="topbar"></div>
  <div class="transient-banner-region" id="transient-banner-region"></div>
  <div class="layout" id="app"></div>
`;

class ChimeTtsSettingsPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    this._app = this.shadowRoot.getElementById("app");
    this._topbar = this.shadowRoot.getElementById("topbar");
    this._transientBannerRegion = this.shadowRoot.getElementById("transient-banner-region");
    this._snowfall = this.shadowRoot.getElementById("snowfall");
    this._modalResizeObserver = null;
    this._data = null;
    this._panelTranslations = {};
    this._draftValues = {};
    this._draftNotifyProfiles = [];
    this._isDirty = false;
    this._clientErrors = {};
    this._notifyProfileClientErrors = [];
    this._loading = true;
    this._saving = false;
    this._saveResult = null;
    this._lastRequested = false;
    this._messageTimeout = null;
    this._scheduledMessageKey = "";
    this._saveResultTimeout = null;
    this._betaClickTimestamp = 0;
    this._betaClickCount = 0;
    this._betaBugTimers = new Set();
    this._picker = null;
    this._pickerLoading = false;
    this._pickerNativeFileDialogOpen = false;
    this._pickerLoadingVisible = false;
    this._pickerLoadingDelayTimer = null;
    this._pickerLoadingToken = 0;
    this._pickerError = null;
    this._pickerBusy = false;
    this._pickerFilter = "";
    this._pickerSelectedPath = "";
    this._pickerAction = null;
    this._pickerMenuOpen = false;
    this._pickerFocusState = null;
    this._pickerScrollState = null;
    this._pickerAudio = null;
    this._pickerAudioObjectUrl = "";
    this._pickerAudioLoadToken = 0;
    this._pickerAudioLoadingPath = "";
    this._pickerPlayingPath = "";
    this._chimeSetWaveformCache = new Map();
    this._chimeSetDurationCache = new Map();
    this._chimeSetWaveformAudioContext = null;
    this._chimeSetWaveformLoadToken = 0;
    this._chimeSetOffsetPreviewAudio = null;
    this._chimeSetOffsetPreviewObjectUrl = "";
    this._chimeSetOffsetPreviewToken = 0;
    this._pickerPreviewDuration = 0;
    this._fieldPreviewAudio = null;
    this._fieldPreviewAudioObjectUrl = "";
    this._fieldPreviewAudioLoadToken = 0;
    this._fieldPreviewLoadingKey = "";
    this._fieldPreviewPlayingKey = "";
    this._fieldPreviewDuration = 0;
    this._notifyPreviewAudio = null;
    this._notifyPreviewAudioObjectUrl = "";
    this._notifyPreviewAudioLoadToken = 0;
    this._notifyPreviewLoadingKey = "";
    this._notifyPreviewPlayingKey = "";
    this._notifyPreviewDuration = 0;
    this._footerLogoSvgMarkup = "";
    this._footerLogoSvgUrl = "";
    this._advancedSections = {};
    this._expandedConfigSections = {};
    this._expandedRandomChimeSets = {};
    this._expandedNotifyProfiles = {};
    this._notifyProfileTests = {};
    this._notifyProfileTestTimers = {};
    this._emptyChimeSetSelection = Math.floor(Math.random() * 3);
    this._emptyChimeSetNextSelection = this._randomEmptyChimeSetSelection(
      this._emptyChimeSetSelection,
    );
    this._emptyChimeSetSpinTimer = null;
    this._expandedLogEvents = {};
    this._logCopyState = {};
    this._logCopyTimers = {};
    this._logsRefreshTimer = null;
    this._logsRefreshInFlight = false;
    this._logsOpeningRefresh = false;
    this._logsLoaded = false;
    this._logsHydrated = false;
    this._logsSubscription = null;
    this._logsSubscriptionPending = false;
    this._debugLogsSubscription = null;
    this._debugLogsSubscriptionPending = false;
    this._deferredLogEvents = [];
    this._debugLogsEnabled = false;
    this._debugLogsUpdating = false;
    this._debugLogsError = "";
    this._boundVisibilityRefresh = () => this._syncLogsRefresh();
    this._boundSelectionRefresh = () => this._syncLogsRefresh();
    this._boundFocusRefresh = () => this._syncLogsRefresh();
    this._boundResizeRefresh = () => {
      this._syncLogEventActionWrapping();
      this._syncModalBounds();
    };
    this._boundBeforeUnload = (event) => this._handleBeforeUnload(event);
    this._boundNavigationClick = (event) => this._handleNavigationClick(event);
    this._boundChapterToggle = (event) => this._handleChapterToggleEvent(event);
    this._pathValidationState = {};
    this._pathValidationTimers = {};
    this._invalidPathOverrides = {};
    this._restartPending = false;
    this._restartConfirmOpen = false;
    this._discardChangesConfirmOpen = false;
    this._randomChimeSetDeleteTarget = null;
    this._chimeSetOffsetEditor = null;
    this._pendingNavigationUrl = "";
    this._pendingRestartReason = null;
    this._allowUnload = false;
    this._restarting = false;
    this._restartContext = null;
    this._expandedChapters = {};
    this._notifyProfilesHydrationRequestId = 0;
    this._pathValidationHydrationRequestId = 0;
    this._hassConnected = null;
  }

  connectedCallback() {
    if (typeof ResizeObserver === "function" && !this._modalResizeObserver) {
      this._modalResizeObserver = new ResizeObserver(() => this._syncModalBounds());
      this._modalResizeObserver.observe(this);
    }
    document.addEventListener("visibilitychange", this._boundVisibilityRefresh);
    document.addEventListener("selectionchange", this._boundSelectionRefresh);
    this.shadowRoot?.addEventListener("focusin", this._boundFocusRefresh);
    this.shadowRoot?.addEventListener("focusout", this._boundFocusRefresh);
    this.shadowRoot?.addEventListener("click", this._boundChapterToggle);
    this.shadowRoot?.addEventListener("keydown", this._boundChapterToggle);
    window.addEventListener("resize", this._boundResizeRefresh);
    window.addEventListener("beforeunload", this._boundBeforeUnload);
    document.addEventListener("click", this._boundNavigationClick, true);
    this._scheduleEmptyChimeSetReelSpin();
  }

  disconnectedCallback() {
    document.removeEventListener("visibilitychange", this._boundVisibilityRefresh);
    document.removeEventListener("selectionchange", this._boundSelectionRefresh);
    this.shadowRoot?.removeEventListener("focusin", this._boundFocusRefresh);
    this.shadowRoot?.removeEventListener("focusout", this._boundFocusRefresh);
    this.shadowRoot?.removeEventListener("click", this._boundChapterToggle);
    this.shadowRoot?.removeEventListener("keydown", this._boundChapterToggle);
    window.removeEventListener("resize", this._boundResizeRefresh);
    window.removeEventListener("beforeunload", this._boundBeforeUnload);
    document.removeEventListener("click", this._boundNavigationClick, true);
    this._teardownLogsSubscription();
    this._teardownDebugLogsSubscription();
    this._clearLogsRefreshTimer();
    this._clearAllNotifyProfileTestTimers();
    this._clearAllLogCopyTimers();
    this._clearEmptyChimeSetReelSpinTimer();
    this._stopPickerAudio();
    this._stopFieldPreviewAudio();
    this._stopNotifyPreviewAudio();
    this._chimeSetWaveformLoadToken += 1;
    this._chimeSetWaveformAudioContext?.close?.();
    this._chimeSetWaveformAudioContext = null;
    for (const timer of this._betaBugTimers) {
      window.clearTimeout(timer);
    }
    this._betaBugTimers.clear();
    this._modalResizeObserver?.disconnect();
    this._modalResizeObserver = null;
  }

  set hass(hass) {
    const wasConnected = this._hassConnected;
    this._hass = hass;
    this._hassConnected = typeof hass?.connected === "boolean" ? hass.connected : null;
    const reconnected = this._lastRequested
      && wasConnected === false
      && this._hassConnected === true
      && !this._loading
      && !this._saving
      && !this._isDirty;
    if (!this._lastRequested) {
      this._lastRequested = true;
      this._load();
      return;
    }
    if (reconnected) {
      this._load();
      return;
    }
    this._syncLiveHassBindings();
  }

  set panel(panel) {
    this._panel = panel;
  }

  set narrow(narrow) {
    const nextNarrow = Boolean(narrow);
    if (this._narrow === nextNarrow) {
      return;
    }
    this._narrow = nextNarrow;
    this.toggleAttribute("narrow", nextNarrow);
    this._syncModalBounds();
    if (!this._loading && !this._saving) {
      this._render();
    }
  }

  set route(route) {
    this._route = route;
  }

  _t(key, replacements = undefined) {
    const translationKey = `component.chime_tts.config_panel.${key}`;
    const fallback = PANEL_TRANSLATION_FALLBACKS[key] || key;
    const translated = this._panelTranslations?.[translationKey]
      || this._hass?.localize?.(translationKey, replacements);
    return Object.entries(replacements || {}).reduce(
      (value, [placeholder, replacement]) => value.replaceAll(`{${placeholder}}`, String(replacement)),
      !translated || translated === translationKey || translated === key ? fallback : translated,
    );
  }

  async _loadPanelTranslations() {
    if (!this._hass?.callWS) {
      return;
    }

    try {
      const language = this._hass.locale?.language || this._hass.language || navigator.language;
      const result = await this._hass.callWS({
        type: "frontend/get_translations",
        language,
        category: "config_panel",
        integration: ["chime_tts"],
      });
      this._panelTranslations = result?.resources || {};
    } catch (_error) {
      this._panelTranslations = {};
    }
  }

  async _load() {
    this._loading = true;
    this._render();
    try {
      await this._loadPanelTranslations();
      this._data = await this._hass.callWS({ type: "chime_tts/get_settings" });
      await this._loadDebugLogsState();
      this._draftValues = { ...(this._data?.values || {}) };
      this._draftNotifyProfiles = this._cloneNotifyProfiles(this._data?.notify_profiles || []);
      this._isDirty = false;
      this._clientErrors = {};
      this._notifyProfileClientErrors = [];
      this._expandedConfigSections = {};
      this._expandedRandomChimeSets = {};
      this._expandedNotifyProfiles = {};
      this._clearAllNotifyProfileTestTimers();
      this._notifyProfileTests = {};
      this._clearAllLogCopyTimers();
      this._logCopyState = {};
      this._expandedLogEvents = {};
      this._logsOpeningRefresh = false;
      this._logsLoaded = false;
      this._logsHydrated = false;
      this._deferredLogEvents = [];
      this._pathValidationState = this._buildInitialPathValidationState();
      this._invalidPathOverrides = {};
      this._restartPending = false;
      this._restartConfirmOpen = false;
      this._restarting = false;
      this._restartContext = null;
      this._expandedChapters = {};
      await this._ensureFooterLogoMarkup(this._data?.footer_logo_url || "");
      await this._ensureLogsSubscription();
      await this._ensureDebugLogsSubscription();
    } catch (error) {
      this._data = {
        sections: [],
        values: {},
        errors: {},
        message: error?.message || this._t("error.load_panel"),
        message_type: "error",
        documentation_url: "https://nimroddolev.github.io/chime_tts/",
        logs_url: "/config/logs?filter=chime_tts",
        fallback_note: "",
        restart_note: "",
      };
      this._draftValues = {};
      this._draftNotifyProfiles = [];
      this._isDirty = false;
      this._clientErrors = {};
      this._notifyProfileClientErrors = [];
      this._expandedConfigSections = {};
      this._expandedRandomChimeSets = {};
      this._expandedNotifyProfiles = {};
      this._clearAllNotifyProfileTestTimers();
      this._notifyProfileTests = {};
      this._clearAllLogCopyTimers();
      this._logCopyState = {};
      this._expandedLogEvents = {};
      this._logsOpeningRefresh = false;
      this._logsLoaded = false;
      this._logsHydrated = false;
      this._deferredLogEvents = [];
      this._pathValidationState = {};
      this._invalidPathOverrides = {};
      this._restartPending = false;
      this._restartConfirmOpen = false;
      this._restarting = false;
      this._restartContext = null;
      this._expandedChapters = {};
      this._footerLogoSvgMarkup = "";
      this._footerLogoSvgUrl = "";
    } finally {
      this._loading = false;
      this._render();
      this._syncLogsRefresh();
      if (this._data && this._data.notify_profiles_hydrated === false) {
        this._hydrateNotifyProfiles();
      }
      this._hydrateInitialPathValidations();
    }
  }

  async _hydrateNotifyProfiles() {
    if (!this._hass || this._loading || this._data?.notify_profiles_hydrated !== false) {
      return;
    }

    const requestId = ++this._notifyProfilesHydrationRequestId;
    try {
      const result = await this._hass.callWS({ type: "chime_tts/get_notify_profiles" });
      if (requestId !== this._notifyProfilesHydrationRequestId) {
        return;
      }

      const nextProfiles = Array.isArray(result?.notify_profiles) ? result.notify_profiles : [];
      const currentSavedProfiles = this._data?.notify_profiles || [];
      const currentDraftProfiles = this._draftNotifyProfiles || [];
      const canAdoptHydratedProfiles = currentSavedProfiles.length === 0
        && currentDraftProfiles.length === 0
        && !this._isDirty;

      this._data = {
        ...(this._data || {}),
        notify_profiles: nextProfiles,
        notify_profiles_hydrated: true,
        notify_profiles_load_error: result?.notify_profiles_load_error || null,
      };
      if (canAdoptHydratedProfiles) {
        this._draftNotifyProfiles = this._cloneNotifyProfiles(nextProfiles);
      }
      this._renderPreservingScrollPosition();
    } catch (error) {
      if (requestId !== this._notifyProfilesHydrationRequestId) {
        return;
      }
      this._data = {
        ...(this._data || {}),
        notify_profiles_hydrated: true,
        notify_profiles_load_error: error?.message || this._t("error.load_profiles"),
      };
      this._renderPreservingScrollPosition();
    }
  }

  _hydrateInitialPathValidations() {
    const pathFields = this._getBrowsableFieldsNeedingValidation();
    if (!this._hass || this._loading || pathFields.length === 0) {
      return;
    }

    const requestId = ++this._pathValidationHydrationRequestId;
    window.setTimeout(async () => {
      if (requestId !== this._pathValidationHydrationRequestId) {
        return;
      }

      for (const field of pathFields) {
        if (requestId !== this._pathValidationHydrationRequestId) {
          return;
        }
        await this._requestPathValidation(field.key, this._draftValues?.[field.key] ?? "", {
          preserveInputState: false,
        });
      }
    }, 0);
  }

  async _ensureLogsSubscription() {
    if (!this._hass?.connection || this._logsSubscription || this._logsSubscriptionPending) {
      return;
    }

    this._logsSubscriptionPending = true;
    try {
      this._logsSubscription = await this._hass.connection.subscribeMessage(
        (message) => this._handleIncomingLogEvent(message?.event?.log_event || message?.log_event),
        { type: "chime_tts/subscribe_logs" },
      );
    } catch (_error) {
      this._logsSubscription = null;
    } finally {
      this._logsSubscriptionPending = false;
    }
  }

  _teardownLogsSubscription() {
    if (typeof this._logsSubscription === "function") {
      this._logsSubscription();
    }
    this._logsSubscription = null;
    this._logsSubscriptionPending = false;
  }

  async _ensureDebugLogsSubscription() {
    if (!this._hass?.connection || this._debugLogsSubscription || this._debugLogsSubscriptionPending) return;
    this._debugLogsSubscriptionPending = true;
    try {
      this._debugLogsSubscription = await this._hass.connection.subscribeMessage(
        (message) => this._handleDebugLogsStatus(message?.event || message),
        { type: "chime_tts/subscribe_debug_log_status" },
      );
    } catch (_error) {
      this._debugLogsSubscription = null;
    } finally {
      this._debugLogsSubscriptionPending = false;
    }
  }

  _teardownDebugLogsSubscription() {
    if (typeof this._debugLogsSubscription === "function") this._debugLogsSubscription();
    this._debugLogsSubscription = null;
    this._debugLogsSubscriptionPending = false;
  }

  _handleDebugLogsStatus(status) {
    if (typeof status?.debug_enabled !== "boolean" || this._debugLogsUpdating) return;
    this._debugLogsEnabled = status.debug_enabled;
    this._debugLogsError = "";
    this._renderPreservingScrollPosition();
  }

  _handleIncomingLogEvent(logEvent) {
    if (!logEvent || !logEvent.id) {
      return;
    }

    if (
      this._picker
      || this._hasActiveInteractiveElement()
    ) {
      this._deferredLogEvents = [
        logEvent,
        ...(this._deferredLogEvents || []).filter((event) => event?.id !== logEvent.id),
      ];
      return;
    }

    const existingEvents = this._data?.log_events || [];
    this._data = {
      ...(this._data || {}),
      log_events: [
        logEvent,
        ...existingEvents.filter((event) => event?.id !== logEvent.id),
      ],
    };
    this._logsLoaded = this._logsHydrated;
    if (this._isChapterExpanded("logs")) {
      this._render();
    }
  }

  _flushDeferredLogEvents() {
    const deferredEvents = this._deferredLogEvents || [];
    if (deferredEvents.length === 0) {
      return false;
    }

    const existingEvents = this._data?.log_events || [];
    const deferredIds = new Set(deferredEvents.map((event) => event?.id).filter(Boolean));
    this._data = {
      ...(this._data || {}),
      log_events: [
        ...deferredEvents,
        ...existingEvents.filter((event) => !deferredIds.has(event?.id)),
      ],
    };
    this._deferredLogEvents = [];
    this._logsLoaded = this._logsHydrated;
    if (this._isChapterExpanded("logs")) {
      this._render();
    }
    return true;
  }

  _renderSnowfall() {
    if (!this._snowfall) {
      return;
    }
    if (!IS_DECEMBER) {
      this._snowfall.innerHTML = "";
      return;
    }
    if (!this._snowfallParticles) {
      this._snowfallParticles = Array.from({ length: 150 }, () => ({
        left: Math.random() * 100,
        size: 2 + Math.random() * 13,
        opacity: 0.55 + Math.random() * 0.35,
        duration: 3 + Math.random() * 13,
        delay: -Math.random() * 20,
        drift: -170 + Math.random() * 240,
      }));
    }
    if (this._snowfall.childElementCount > 0) {
      return;
    }
    this._snowfall.innerHTML = this._snowfallParticles
      .map(
        (particle) => `
          <span
            class="snowflake-particle"
            style="--snow-left:${particle.left.toFixed(2)}%;--snow-size:${particle.size.toFixed(1)}px;--snow-opacity:${particle.opacity.toFixed(2)};--snow-duration:${particle.duration.toFixed(1)}s;--snow-delay:${particle.delay.toFixed(1)}s;--snow-drift:${particle.drift.toFixed(0)}px"
          >${SNOWFLAKE_SVG}</span>`,
      )
      .join("");
  }

  _render({ force = false } = {}) {
    const activeControl = this.shadowRoot?.activeElement;
    if (!force && !this._loading && this._isTextEntryOrDropdown(activeControl)) {
      this._renderTopbar(this._data || {});
      this._deferPanelRenderUntilBlur(activeControl);
      return;
    }

    if (this._loading) {
      this._snowfall.innerHTML = "";
      this._renderTopbar({});
      this._renderTransientMessage({});
      this._app.innerHTML = `<div class="loading" role="status" aria-label="${this._escapeAttribute(this._t("loading.settings"))}"><span class="loading-spinner" aria-hidden="true"></span></div>`;
      return;
    }

    this._renderSnowfall();

    const shouldPreservePickerScroll = Boolean(
      this._picker && this.shadowRoot.querySelector(".picker-filebrowser-table-wrap"),
    );
    if (shouldPreservePickerScroll && !this._pickerScrollState) {
      this._pickerScrollState = this._capturePickerScrollState();
    }

    const data = this._data || {};
    const sections = data.sections || [];
    const values = this._draftValues || {};
    const errors = { ...(data.errors || {}), ...(this._clientErrors || {}) };
    const alertsMarkup = this._renderPanelAlerts(data.alerts || []);
    const notifyProfilesLoadError = data.notify_profiles_load_error
      ? `<div class="message error">${this._escapeHtml(data.notify_profiles_load_error)}</div>`
      : "";
    const isLoadFailureState = data.message_type === "error" && sections.length === 0;
    this._renderTopbar(data);
    this._renderTransientMessage(data, sections.length);

    this._app.innerHTML = `
      ${alertsMarkup}
      ${notifyProfilesLoadError}
      ${isLoadFailureState
        ? `
          <div class="error-recovery">
            <button class="button-primary" type="button" data-reload-panel="1">${this._escapeHtml(this._t("action.reload"))}</button>
          </div>
        `
        : `
          <form id="settings-form">
            ${this._renderSettingsContent(sections, values, errors, data)}
            <div class="footer">
              ${this._renderPageFooter(data)}
            </div>
          </form>
        `
      }
      ${this._renderPicker()}
      ${this._renderRestartConfirmation()}
      ${this._renderDiscardChangesConfirmation()}
      ${this._renderRandomChimeSetDeleteConfirmation()}
      ${this._renderChimeSetOffsetEditor()}
    `;
    this._syncModalBounds();

    this.shadowRoot.getElementById("settings-form")?.addEventListener("submit", (event) => {
      event.preventDefault();
      this._submit();
    });
    this._syncFooterLogoTransparency();
    this._wireFooterLogoAnimation();
    this.shadowRoot.querySelectorAll("[data-reload-panel]").forEach((button) => {
      button.addEventListener("click", () => this._load());
    });
    this.shadowRoot.querySelectorAll("[data-reset-section]").forEach((button) => {
      button.addEventListener("click", (event) => this._resetSection(event.currentTarget.dataset.resetSection));
    });
    this.shadowRoot.querySelectorAll("[data-config-section-card]").forEach((card) => {
      card.addEventListener("click", (event) => {
        if (this._shouldIgnoreConfigSectionCardToggle(event)) {
          return;
        }
        event.stopPropagation();
        this._toggleConfigSection(event.currentTarget.dataset.configSectionCard);
      });
      card.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
          return;
        }
        if (this._shouldIgnoreConfigSectionCardToggle(event)) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        this._toggleConfigSection(event.currentTarget.dataset.configSectionCard);
      });
    });
    this.shadowRoot.querySelectorAll("[data-toggle-config-section]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this._toggleConfigSection(event.currentTarget.dataset.toggleConfigSection);
      });
    });
    this.shadowRoot.querySelectorAll("[data-toggle-advanced]").forEach((button) => {
      button.addEventListener("click", (event) => this._toggleAdvanced(event.currentTarget.dataset.toggleAdvanced));
    });
    this.shadowRoot.querySelectorAll("[data-field]").forEach((field) => {
      const eventName = field.tagName === "SELECT" || field.type === "checkbox"
        ? "change"
        : "input";
      field.addEventListener(eventName, (event) => this._handleFieldChange(event));
    });
    if (!this._panelFocusListenersBound) {
      this._panelFocusListenersBound = true;
      this._app.addEventListener("focusin", () => this._syncLogsRefresh());
      this._app.addEventListener("focusout", () => {
        window.setTimeout(() => this._syncLogsRefresh(), 0);
      });
    }
    this.shadowRoot.querySelectorAll("[data-add-random-chime-set]").forEach((button) => {
      button.addEventListener("click", () => this._addRandomChimeSet());
    });
    this.shadowRoot.querySelectorAll("[data-random-set-name]").forEach((field) => {
      field.addEventListener("input", (event) => this._updateRandomChimeSetName(Number(event.currentTarget.dataset.randomSetName), event.currentTarget.value));
    });
    this.shadowRoot.querySelectorAll("[data-random-set-member]").forEach((field) => {
      field.addEventListener("change", (event) => this._toggleRandomChimeSetMember(Number(event.currentTarget.dataset.randomSetMember), event.currentTarget.value, event.currentTarget.checked));
    });
    this.shadowRoot.querySelectorAll("[data-edit-chime-set-offset]").forEach((button) => {
      button.addEventListener("click", (event) => this._openChimeSetOffsetEditor(Number(event.currentTarget.dataset.editChimeSetOffset), event.currentTarget.dataset.chimeSetMember, event.currentTarget.dataset.chimeSetMemberLabel));
    });
    this.shadowRoot.querySelectorAll("[data-edit-chime-offset]").forEach((button) => {
      button.addEventListener("click", (event) => this._openChimeOffsetEditor(event.currentTarget.dataset.editChimeOffset, event.currentTarget.dataset.chimeOffsetLabel));
    });
    this.shadowRoot.querySelectorAll("[data-chime-set-offset-reset]").forEach((button) => button.addEventListener("click", () => this._resetChimeSetOffsetEditor()));
    this.shadowRoot.querySelectorAll("[data-chime-set-offset-value]").forEach((button) => {
      button.addEventListener("click", () => this._editChimeSetOffsetValue());
    });
    this.shadowRoot.querySelectorAll("[data-chime-set-offset-input]").forEach((input) => {
      input.addEventListener("input", (event) => this._handleChimeSetOffsetInput(event));
      input.addEventListener("change", (event) => this._handleChimeSetOffsetInput(event));
    });
    this.shadowRoot.querySelectorAll("[data-chime-set-offset-timeline]").forEach((timeline) => {
      this._positionChimeSetOffsetTimeline(timeline);
      timeline.querySelectorAll("[data-chime-set-offset-audio]").forEach((audio) => {
        audio.addEventListener("pointerdown", (event) => this._startChimeSetOffsetDrag(event));
        audio.addEventListener("keydown", (event) => this._handleChimeSetOffsetAudioKeydown(event));
      });
    });
    this.shadowRoot.querySelectorAll("[data-chime-set-offset-close]").forEach((button) => button.addEventListener("click", () => this._closeChimeSetOffsetEditor()));
    this.shadowRoot.querySelectorAll("[data-chime-set-offset-preview]").forEach((button) => button.addEventListener("click", () => this._toggleChimeSetOffsetPreview()));
    this.shadowRoot.querySelectorAll("[data-delete-random-chime-set]").forEach((button) => {
      button.addEventListener("click", (event) => this._requestRandomChimeSetDelete(Number(event.currentTarget.dataset.deleteRandomChimeSet)));
    });
    this.shadowRoot.querySelectorAll("[data-random-chime-set-delete-cancel]").forEach((button) => {
      button.addEventListener("click", () => this._closeRandomChimeSetDeleteConfirmation());
    });
    this.shadowRoot.querySelectorAll("[data-random-chime-set-delete-confirm]").forEach((button) => {
      button.addEventListener("click", () => this._confirmRandomChimeSetDelete());
    });
    this.shadowRoot.querySelectorAll("[data-random-chime-audio-toggle]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        this._toggleFieldPreviewAudio("chime_path", event.currentTarget.dataset.randomChimeAudioToggle);
      });
    });
    this.shadowRoot.querySelectorAll("[data-random-chime-set-header]").forEach((header) => {
      header.addEventListener("click", (event) => {
        const target = event.target;
        if (target instanceof Element && target.closest("button, input, label, .notify-profile-actions")) return;
        this._toggleRandomChimeSet(Number(event.currentTarget.dataset.randomChimeSetHeader));
      });
    });
    this.shadowRoot.querySelectorAll("[data-toggle-random-chime-set]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this._toggleRandomChimeSet(Number(event.currentTarget.dataset.toggleRandomChimeSet));
      });
    });
    this.shadowRoot.querySelectorAll("[data-notify-field]").forEach((field) => {
      const eventName = field.tagName === "SELECT" || field.type === "checkbox"
        ? "change"
        : "input";
      field.addEventListener(eventName, (event) => this._handleNotifyProfileFieldChange(event));
    });
    this.shadowRoot.querySelectorAll("[data-notify-audio-toggle]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        this._toggleNotifyPreviewAudio(
          Number(event.currentTarget.dataset.notifyIndex),
          event.currentTarget.dataset.notifyAudioToggle,
          event.currentTarget.dataset.notifyAudioValue,
        );
      });
    });
    this._wireNotifyEntityPickers();
    this.shadowRoot.querySelectorAll("[data-notify-range]").forEach((field) => {
      field.addEventListener("input", (event) => this._handleNotifyRangeInput(event));
      field.addEventListener("change", (event) => this._handleNotifyRangeCommit(event));
    });
    this.shadowRoot.querySelectorAll("[data-notify-range-number]").forEach((field) => {
      field.addEventListener("input", (event) => this._handleNotifyRangeNumberInput(event));
      field.addEventListener("change", (event) => this._handleNotifyRangeNumberCommit(event));
    });
    this.shadowRoot.querySelectorAll("[data-reset-notify-field]").forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        this._resetNotifyProfileField(
          Number(event.currentTarget.dataset.notifyIndex),
          event.currentTarget.dataset.resetNotifyField,
        );
      });
    });
    this.shadowRoot.querySelectorAll("[data-add-notify-profile]").forEach((button) => {
      button.addEventListener("click", () => this._addNotifyProfile());
    });
    this.shadowRoot.querySelectorAll("[data-remove-notify-profile]").forEach((button) => {
      button.addEventListener("click", (event) => {
        this._removeNotifyProfile(Number(event.currentTarget.dataset.removeNotifyProfile));
      });
    });
    this.shadowRoot.querySelectorAll("[data-notify-profile-card]").forEach((card) => {
      card.addEventListener("click", (event) => {
        if (this._shouldIgnoreNotifyProfileCardToggle(event)) {
          return;
        }
        event.stopPropagation();
        this._toggleNotifyProfile(Number(event.currentTarget.dataset.notifyProfileCard));
      });
      card.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
          return;
        }
        if (this._shouldIgnoreNotifyProfileCardToggle(event)) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        this._toggleNotifyProfile(Number(event.currentTarget.dataset.notifyProfileCard));
      });
    });
    this.shadowRoot.querySelectorAll("[data-toggle-notify-profile]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this._toggleNotifyProfile(Number(event.currentTarget.dataset.toggleNotifyProfile));
      });
    });
    this.shadowRoot.querySelectorAll("[data-remove-notify-entity]").forEach((button) => {
      button.addEventListener("click", (event) => {
        this._removeNotifyEntity(
          Number(event.currentTarget.dataset.notifyIndex),
          event.currentTarget.dataset.removeNotifyEntity,
        );
      });
    });
    this.shadowRoot.querySelectorAll("[data-open-notify-test]").forEach((button) => {
      button.addEventListener("click", (event) => {
        this._openNotifyProfileTest(Number(event.currentTarget.dataset.openNotifyTest));
      });
    });
    this.shadowRoot.querySelectorAll("[data-reset-notify-profile]").forEach((button) => {
      button.addEventListener("click", (event) => {
        this._resetNotifyProfile(Number(event.currentTarget.dataset.resetNotifyProfile));
      });
    });
    this.shadowRoot.querySelectorAll("[data-close-notify-test]").forEach((button) => {
      button.addEventListener("click", (event) => {
        this._closeNotifyProfileTest(Number(event.currentTarget.dataset.closeNotifyTest));
      });
    });
    this.shadowRoot.querySelectorAll("[data-notify-inline-test-message]").forEach((field) => {
      field.addEventListener("input", (event) => {
        this._handleNotifyProfileTestMessageInput(event);
      });
    });
    this.shadowRoot.querySelectorAll("[data-run-notify-inline-test]").forEach((button) => {
      button.addEventListener("click", (event) => {
        this._runNotifyProfileTest(Number(event.currentTarget.dataset.runNotifyInlineTest));
      });
    });
    this.shadowRoot.querySelectorAll("[data-browse-field]").forEach((button) => {
      button.addEventListener("click", (event) => this._openPicker(event.currentTarget.dataset.browseField));
    });
    this.shadowRoot.querySelectorAll("[data-field-audio-toggle]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        this._toggleFieldPreviewAudio(
          event.currentTarget.dataset.fieldAudioToggle,
          event.currentTarget.dataset.fieldAudioValue,
        );
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-nav]").forEach((button) => {
      button.addEventListener("click", (event) => this._loadPicker(event.currentTarget.dataset.pickerNav));
    });
    this.shadowRoot.querySelectorAll("[data-picker-path]").forEach((button) => {
      button.addEventListener("click", (event) => this._loadPicker(event.currentTarget.dataset.pickerPath));
    });
    this.shadowRoot.querySelectorAll("[data-picker-root]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        this._pickerMenuOpen = false;
        this._loadPicker(event.currentTarget.dataset.pickerRoot);
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-open]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        this._pickerMenuOpen = false;
        this._loadPicker(event.currentTarget.dataset.pickerOpen);
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-select]").forEach((button) => {
      button.addEventListener("click", (event) => {
        if (event.target instanceof Element && event.target.closest("[data-picker-open], [data-picker-rename], [data-picker-delete], [data-picker-audio-toggle]")) {
          return;
        }
        event.preventDefault();
        const path = event.currentTarget.dataset.pickerSelect;
        const kind = event.currentTarget.dataset.pickerSelectKind || "directory";
        if (kind === "directory" && event.currentTarget.classList.contains("folder")) {
          this._pickerMenuOpen = false;
          this._loadPicker(path);
          return;
        }
        this._selectPickerPath(path, kind);
      });
      button.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
          return;
        }
        if (event.target instanceof Element && event.target.closest("[data-picker-open], [data-picker-rename], [data-picker-delete], [data-picker-audio-toggle]")) {
          return;
        }
        event.preventDefault();
        const path = event.currentTarget.dataset.pickerSelect;
        const kind = event.currentTarget.dataset.pickerSelectKind || "directory";
        if (kind === "directory" && event.currentTarget.classList.contains("folder")) {
          this._pickerMenuOpen = false;
          this._loadPicker(path);
          return;
        }
        this._selectPickerPath(path, kind);
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-refresh]").forEach((button) => {
      button.addEventListener("click", () => {
        this._pickerMenuOpen = false;
        this._loadPicker(this._picker?.current_path || "");
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-audio-toggle]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        this._togglePickerAudio(
          event.currentTarget.dataset.pickerAudioToggle,
          event.currentTarget.dataset.pickerAudioUrl,
        );
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-filter]").forEach((field) => {
      field.addEventListener("input", (event) => {
        this._pickerFilter = event.currentTarget.value || "";
        this._pickerFocusState = {
          target: "picker-filter",
          start: typeof event.currentTarget.selectionStart === "number" ? event.currentTarget.selectionStart : null,
          end: typeof event.currentTarget.selectionEnd === "number" ? event.currentTarget.selectionEnd : null,
        };
        this._renderPreservingPickerScroll();
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-menu-toggle]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        this._pickerMenuOpen = !this._pickerMenuOpen;
        this._render();
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-new-folder]").forEach((button) => {
      button.addEventListener("click", () => {
        this._pickerMenuOpen = false;
        this._createPickerFolder();
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-rename]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        this._renamePickerEntry(
          event.currentTarget.dataset.pickerRename,
          event.currentTarget.dataset.pickerName || "",
        );
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-delete]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        this._deletePickerEntry(
          event.currentTarget.dataset.pickerDelete,
          event.currentTarget.dataset.pickerName || "",
        );
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-upload-files]").forEach((button) => {
      button.addEventListener("click", () => {
        this._openNativePickerFileDialog({ directory: false });
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-upload-folder]").forEach((button) => {
      button.addEventListener("click", () => {
        this._openNativePickerFileDialog({ directory: true });
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-file-input]").forEach((input) => {
      input.addEventListener("change", (event) => this._handlePickerUploadSelection(event, { directory: false }));
      input.addEventListener("cancel", () => this._closeNativePickerFileDialog());
    });
    this.shadowRoot.querySelectorAll("[data-picker-folder-input]").forEach((input) => {
      input.addEventListener("change", (event) => this._handlePickerUploadSelection(event, { directory: true }));
      input.addEventListener("cancel", () => this._closeNativePickerFileDialog());
    });
    this.shadowRoot.querySelectorAll("[data-picker-close]").forEach((button) => {
      button.addEventListener("click", () => this._closePicker());
    });
    this.shadowRoot.querySelectorAll("[data-picker-overlay]").forEach((overlay) => {
      overlay.addEventListener("click", (event) => {
        if (event.target === event.currentTarget) {
          this._closePicker();
        }
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-choose]").forEach((button) => {
      button.addEventListener("click", (event) => this._choosePickerPath(event.currentTarget.dataset.pickerChoose));
    });
    this.shadowRoot.querySelectorAll("[data-picker-action-cancel]").forEach((button) => {
      button.addEventListener("click", () => this._closePickerAction());
    });
    this.shadowRoot.querySelectorAll("[data-picker-action-secondary]").forEach((button) => {
      button.addEventListener("click", () => this._runPickerActionSecondary());
    });
    this.shadowRoot.querySelectorAll("[data-picker-action-input]").forEach((input) => {
      input.addEventListener("input", (event) => {
        if (!this._pickerAction) {
          return;
        }
        this._pickerAction = {
          ...this._pickerAction,
          value: event.currentTarget.value || "",
          error: "",
        };
      });
      input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          this._submitPickerAction();
        }
      });
      window.setTimeout(() => input.focus(), 0);
      if (typeof input.select === "function") {
        window.setTimeout(() => input.select(), 0);
      }
    });
    this.shadowRoot.querySelectorAll("[data-picker-action-submit]").forEach((button) => {
      button.addEventListener("click", () => this._submitPickerAction());
    });
    this.shadowRoot.querySelectorAll("[data-restart-open]").forEach((button) => {
      button.addEventListener("click", (event) => this._openRestartConfirmation(event.currentTarget.dataset.restartOpen));
    });
    this.shadowRoot.querySelectorAll("[data-restart-cancel]").forEach((button) => {
      button.addEventListener("click", () => this._closeRestartConfirmation());
    });
    this.shadowRoot.querySelectorAll("[data-restart-confirm]").forEach((button) => {
      button.addEventListener("click", () => this._confirmRestart());
    });
    this.shadowRoot.querySelectorAll("[data-discard-changes-cancel]").forEach((button) => {
      button.addEventListener("click", () => this._closeDiscardChangesConfirmation());
    });
    this.shadowRoot.querySelectorAll("[data-discard-changes-confirm]").forEach((button) => {
      button.addEventListener("click", () => this._confirmResetAllChanges());
    });
    this.shadowRoot.querySelectorAll("[data-discard-changes-save]").forEach((button) => {
      button.addEventListener("click", () => this._saveUnsavedChanges());
    });
    this.shadowRoot.querySelectorAll("[data-use-anyway]").forEach((button) => {
      button.addEventListener("click", (event) => this._useInvalidPathAnyway(event.currentTarget.dataset.useAnyway));
    });
    this.shadowRoot.querySelectorAll("[data-set-path]").forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        this._setPathSuggestion(
          event.currentTarget.dataset.setPath,
          event.currentTarget.dataset.pathValue,
        );
      });
    });
    this.shadowRoot.querySelectorAll(".chapter-hero-toggle a").forEach((link) => {
      link.addEventListener("click", (event) => {
        event.stopPropagation();
      });
    });
    this.shadowRoot.querySelectorAll(".chapter-hero-actions button").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
      });
    });
    this.shadowRoot.querySelectorAll("[data-toggle-log-event]").forEach((row) => {
      row.addEventListener("click", (event) => {
        if (event.target instanceof Element && event.target.closest(".log-event-body")) {
          return;
        }
        this._toggleLogEvent(event.currentTarget.dataset.toggleLogEvent);
      });
      row.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          this._toggleLogEvent(event.currentTarget.dataset.toggleLogEvent);
        }
      });
    });
    this.shadowRoot.querySelectorAll("[data-copy-log-yaml]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this._copyLogYaml(event.currentTarget.dataset.copyLogYaml);
      });
    });
    this.shadowRoot.querySelectorAll("[data-copy-log-raw]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this._copyLogRaw(event.currentTarget.dataset.copyLogRaw);
      });
    });
    this.shadowRoot.querySelectorAll("[data-repeat-log-action]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this._repeatLogAction(event.currentTarget.dataset.repeatLogAction);
      });
    });
    this.shadowRoot.querySelectorAll("[data-toggle-all-logs]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this._toggleAllLogEvents(event.currentTarget.dataset.toggleAllLogs);
      });
    });
    this.shadowRoot.querySelectorAll("[data-toggle-debug-logs]").forEach((toggle) => {
      toggle.addEventListener("change", (event) => {
        this._setDebugLogsEnabled(event.currentTarget.checked);
      });
    });
    this.shadowRoot.querySelectorAll("[data-toggle-log-arrow]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this._toggleLogEvent(event.currentTarget.dataset.toggleLogArrow);
      });
    });
    this._syncLogEventActionWrapping();
    window.requestAnimationFrame(() => this._syncLogEventActionWrapping());
    this._syncLogsRefresh();
    if (shouldPreservePickerScroll) {
      this._restorePickerScrollState();
    }
    this._restoreTransientFocus();
  }

  _syncModalBounds() {
    if (!this.isConnected) {
      return;
    }

    const rect = this.getBoundingClientRect();
    const viewportWidth = window.innerWidth || document.documentElement?.clientWidth || 0;
    const viewportHeight = window.innerHeight || document.documentElement?.clientHeight || 0;
    const left = Math.max(0, rect.left);
    const top = Math.max(0, rect.top);
    const right = Math.min(viewportWidth, rect.right);
    const bottom = Math.min(viewportHeight, rect.bottom);
    const width = Math.max(0, right - left);
    const height = Math.max(0, bottom - top);

    this.style.setProperty("--modal-left", `${left}px`);
    this.style.setProperty("--modal-top", `${top}px`);
    this.style.setProperty("--modal-width", `${width}px`);
    this.style.setProperty("--modal-height", `${height}px`);
    const timeline = this.shadowRoot?.querySelector("[data-chime-set-offset-timeline]");
    if (timeline) this._positionChimeSetOffsetTimeline(timeline);
  }

  _renderPanelAlerts(alerts) {
    if (!Array.isArray(alerts) || alerts.length === 0) {
      return "";
    }

    return `
      <div class="panel-alerts">
        ${alerts.map((alert) => this._renderPanelAlert(alert)).join("")}
      </div>
    `;
  }

  _renderPanelAlert(alert) {
    if (!alert || !alert.message) {
      return "";
    }

    const tone = alert.tone === "error" ? "error" : "warning";
    const action = alert.action || null;
    const message = alert.message_html
      ? this._sanitizePanelAlertHtml(alert.message_html)
      : this._renderPanelAlertMessage(alert.message, alert.highlighted_terms || []);
    return `
      <div class="panel-alert ${this._escapeAttribute(tone)}" role="alert">
        <div class="panel-alert-copy">
          <span class="panel-alert-icon" aria-hidden="true">${ICONS.alert}</span>
          <div class="panel-alert-text">
            ${alert.title ? `<p class="panel-alert-title">${this._escapeHtml(alert.title)}</p>` : ""}
            <p class="panel-alert-message">${message}</p>
          </div>
        </div>
        ${action?.kind === "restart"
          ? `<button class="button-secondary panel-alert-action" type="button" data-restart-open="provider-refresh" ${this._restarting ? "disabled" : ""}>${this._escapeHtml(action.label || "Restart")}</button>`
          : action?.kind === "link" && action?.href
          ? `<a class="button-primary panel-alert-action" href="${this._escapeAttribute(action.href)}">${this._escapeHtml(action.label || "Open")}</a>`
          : ""
        }
      </div>
    `;
  }

  _renderPanelAlertMessage(message, highlightedTerms = []) {
    const escapedMessage = this._escapeHtml(String(message || ""));
    if (!Array.isArray(highlightedTerms) || highlightedTerms.length === 0) {
      return escapedMessage;
    }

    let renderedMessage = escapedMessage;
    const uniqueTerms = [...new Set(highlightedTerms.map((term) => String(term || "")).filter(Boolean))];
    for (const term of uniqueTerms) {
      const escapedTerm = this._escapeHtml(term);
      renderedMessage = renderedMessage.replaceAll(
        escapedTerm,
        `<strong>${escapedTerm}</strong>`,
      );
    }
    return renderedMessage;
  }

  _sanitizePanelAlertHtml(messageHtml) {
    const html = String(messageHtml || "");
    return html.replace(/<(?!\/?strong\b)[^>]*>/gi, "");
  }

  _renderTopbar(data) {
    const version = String(data?.version || "");
    const isBetaVersion = /-beta[^/\\\s]*$/i.test(version);
    this._topbar.innerHTML = `
      <div>
        <div class="topbar">
          ${this._narrow
            ? `
              <div class="topbar-nav">
                <button class="topbar-menu" type="button" data-open-ha-menu="1" aria-label="Open navigation menu" title="Open navigation menu">${ICONS.moreVertical}</button>
              </div>
            `
            : ""
          }
          <div class="topbar-main">
            <div class="topbar-text">
              <p class="topbar-title">
                <span class="topbar-title-brand">${IS_DECEMBER ? `<span class="topbar-santa-hat">${SANTA_HAT_SVG}</span>` : ""}Chime TTS${isBetaVersion ? '<span class="topbar-beta-badge" role="button" tabindex="0" aria-label="BETA easter egg">BETA</span>' : ""}</span>
              </p>
            </div>
          </div>
          <div class="topbar-actions">
            ${this._isDirty
              ? `<button class="button-secondary" type="button" data-reset-all="1">${this._escapeHtml(this._t("action.reset"))}</button>`
              : ""
            }
            ${this._saveResult && (this._saveResult !== "success" || !this._isDirty)
              ? `
                <div class="save-slot">
                  <span class="save-status ${this._escapeAttribute(this._saveResult)}" aria-live="polite">${this._saveResult === "success" ? "&#10003;" : "X"}</span>
                </div>
              `
              : this._saving
                ? `
                  <div class="save-slot">
                    <button class="button-primary is-saving" type="button" disabled aria-busy="true" aria-label="${this._escapeAttribute(this._t("action.save"))}"><span class="button-spinner" aria-hidden="true"></span></button>
                  </div>
                `
              : this._restartPending && !this._isDirty
                ? `
                  <div class="save-slot">
                    <button class="button-restart" type="button" data-restart-open="pending" ${this._restarting ? "disabled" : ""}>${this._escapeHtml(this._t("action.restart"))}</button>
                  </div>
                `
                : this._isDirty
                  ? `
                    <div class="save-slot">
                      <button class="button-primary" id="save-top" type="button" ${this._saving || this._hasInvalidPathChanges() ? "disabled" : ""}>${this._escapeHtml(this._t("action.save"))}</button>
                    </div>
                  `
                  : ""
            }
          </div>
        </div>
      </div>
    `;
    const saveButton = this.shadowRoot.getElementById("save-top");
    saveButton?.addEventListener("pointerdown", (event) => {
      // Start the save before the browser's default focus change can remove
      // this button. _submitFromSaveButton deliberately blurs and restores
      // the active control around the save operation.
      event.preventDefault();
      void this._submitFromSaveButton();
    });
    saveButton?.addEventListener("click", (event) => {
      // Pointer activation was handled above; detail 0 represents keyboard
      // and assistive-technology activation.
      if (event.detail === 0) {
        void this._submitFromSaveButton();
      }
    });
    this.shadowRoot.querySelectorAll("[data-open-ha-menu]").forEach((button) => {
      button.addEventListener("click", () => this._toggleHassMenu());
    });
    this.shadowRoot.querySelectorAll("[data-reset-all]").forEach((button) => {
      button.addEventListener("click", () => this._requestResetAllChanges());
    });
    const betaBadge = this.shadowRoot.querySelector(".topbar-beta-badge");
    betaBadge?.addEventListener("click", (event) => this._handleBetaBadgeClick(event));
    betaBadge?.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        this._handleBetaBadgeClick(event);
      }
    });
  }

  _handleBetaBadgeClick(event) {
    const badge = event.currentTarget;
    if (!(badge instanceof HTMLElement)) {
      return;
    }

    const timestamp = Date.now();
    this._betaClickCount = timestamp - this._betaClickTimestamp <= 250
      ? this._betaClickCount + 1
      : 1;
    this._betaClickTimestamp = timestamp;

    badge.classList.remove("is-shaking");
    void badge.offsetWidth;
    badge.classList.add("is-shaking");

    if (this._betaClickCount >= 5) {
      this._betaClickCount = 0;
      this._releaseBetaBug(badge);
    }
  }

  _releaseBetaBug(badge) {
    const topbar = badge.closest(".topbar");
    if (!(topbar instanceof HTMLElement)) {
      return;
    }

    const badgeRect = badge.getBoundingClientRect();
    const bug = document.createElement("span");
    bug.className = "topbar-beta-bug";
    bug.setAttribute("aria-hidden", "true");
    bug.innerHTML = '<svg viewBox="0 0 22 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 5.5 1 3.5M4 8.5 1.5 10.5M9 4 7.5 1.5M9 10 7.5 12.5M15 4 16.5 1.5M15 10 16.5 12.5M19 5.5 21 3.5M19 8.5 21 10.5" stroke="#1f2937" stroke-width="1.4" stroke-linecap="round"/><ellipse cx="6" cy="7" rx="3.5" ry="3.1" fill="#4b5563"/><ellipse cx="12" cy="7" rx="3.7" ry="3.2" fill="#374151"/><ellipse cx="17.5" cy="7" rx="3" ry="3.1" fill="#111827"/><circle cx="18.5" cy="6" r=".55" fill="#f8fafc"/></svg>';
    const bugLeft = badgeRect.left + (badgeRect.width - 22) / 2;
    bug.style.setProperty("--beta-bug-left", `${bugLeft}px`);
    bug.style.setProperty("--beta-bug-top", `${badgeRect.bottom}px`);
    bug.style.setProperty("--beta-bug-drop", "0px");
    const crawlDistance = Math.max(0, window.innerWidth - bugLeft + 48);
    bug.style.setProperty("--beta-bug-crawl", `${crawlDistance}px`);
    this.shadowRoot.appendChild(bug);

    const cleanupTimer = window.setTimeout(() => {
      bug.remove();
      this._betaBugTimers.delete(cleanupTimer);
    }, 2600);
    this._betaBugTimers.add(cleanupTimer);
  }

  _restoreTransientFocus() {
    const focusState = this._pickerFocusState;
    if (!focusState?.target || !this.shadowRoot) {
      return;
    }

    if (focusState.target === "picker-filter") {
      const field = this.shadowRoot.querySelector("[data-picker-filter]");
      if (!(field instanceof HTMLInputElement)) {
        return;
      }

      field.focus();
      if (typeof focusState.start === "number" && typeof focusState.end === "number") {
        field.setSelectionRange(focusState.start, focusState.end);
      }
    }

    this._pickerFocusState = null;
  }

  _syncLogEventActionWrapping() {
    if (!this.shadowRoot) {
      return;
    }

    const logRows = Array.from(this.shadowRoot.querySelectorAll(".log-event-row"));
    for (const row of logRows) {
      if (!(row instanceof HTMLElement)) {
        continue;
      }
      const main = row.querySelector(".log-event-row-main");
      const actions = row.querySelector(".log-event-actions");
      if (!(main instanceof HTMLElement) || !(actions instanceof HTMLElement)) {
        row.classList.remove("actions-wrapped");
        continue;
      }

      // Measure the natural flex layout before applying the full-width wrapped style.
      row.classList.remove("actions-wrapped");
      const wrapped = actions.offsetTop > main.offsetTop + 2;
      row.classList.toggle("actions-wrapped", wrapped);
    }
  }

  _capturePickerScrollState() {
    if (!this.shadowRoot || !this._picker) {
      return null;
    }

    const scrollHost = this.shadowRoot.querySelector(".picker-filebrowser-table-wrap");
    if (!(scrollHost instanceof HTMLElement)) {
      return null;
    }

    const anchorCandidates = [];
    const rowElements = Array.from(scrollHost.querySelectorAll("[data-picker-row-path]"));
    for (const row of rowElements) {
      if (!(row instanceof HTMLElement)) {
        continue;
      }
      if (row.offsetTop + row.offsetHeight > scrollHost.scrollTop) {
        anchorCandidates.push({
          path: row.dataset.pickerRowPath || "",
          rowIndex: Number(row.dataset.pickerRowIndex || anchorCandidates.length),
          relativeTop: row.offsetTop - scrollHost.scrollTop,
        });
        if (anchorCandidates.length >= 3) {
          break;
        }
      }
    }

    return {
      top: scrollHost.scrollTop,
      left: scrollHost.scrollLeft,
      anchorCandidates,
    };
  }

  _applyPickerScrollStateToHost(scrollHost, scrollState) {
    if (!(scrollHost instanceof HTMLElement) || !scrollState) {
      return;
    }

    const candidates = Array.isArray(scrollState.anchorCandidates)
      ? scrollState.anchorCandidates
      : [];

    for (const candidate of candidates) {
      let anchorRow = null;
      if (candidate?.path) {
        anchorRow = scrollHost.querySelector(
          `[data-picker-row-path="${this._escapeSelectorValue(candidate.path)}"]`,
        );
      }
      if (!(anchorRow instanceof HTMLElement) && Number.isInteger(candidate?.rowIndex)) {
        const rowElements = Array.from(scrollHost.querySelectorAll("[data-picker-row-path]"));
        anchorRow = rowElements[Math.min(
          Math.max(0, candidate.rowIndex),
          Math.max(0, rowElements.length - 1),
        )];
      }
      if (anchorRow instanceof HTMLElement) {
        scrollHost.scrollTop = Math.max(0, anchorRow.offsetTop - candidate.relativeTop);
        scrollHost.scrollLeft = scrollState.left;
        return;
      }
    }

    scrollHost.scrollTop = scrollState.top;
    scrollHost.scrollLeft = scrollState.left;
  }

  _restorePickerScrollState() {
    const scrollState = this._pickerScrollState;
    if (!scrollState || !this.shadowRoot || !this._picker) {
      return;
    }

    const scrollHost = this.shadowRoot.querySelector(".picker-filebrowser-table-wrap");
    if (scrollHost instanceof HTMLElement) {
      this._applyPickerScrollStateToHost(scrollHost, scrollState);
      window.requestAnimationFrame(() => {
        if (!this._picker || !this.shadowRoot) {
          return;
        }
        const nextScrollHost = this.shadowRoot.querySelector(".picker-filebrowser-table-wrap");
        if (nextScrollHost instanceof HTMLElement) {
          this._applyPickerScrollStateToHost(nextScrollHost, scrollState);
        }
      });
    }
    this._pickerScrollState = null;
  }

  _renderPreservingPickerScroll() {
    this._pickerScrollState = this._capturePickerScrollState();
    // Picker filtering happens while the search input is focused. Force this
    // render so the normal text-entry render deferral does not leave the rows
    // showing the unfiltered listing.
    this._render({ force: true });
    this._restorePickerScrollState();
  }

  _renderSection(section, values, errors) {
    if (section.kind === "chime_sets") {
      return this._renderRandomChimeSetsSection(section, errors.chime_sets);
    }
    if (section.kind === "notify_profiles") {
      return this._renderNotifyProfilesSection(section);
    }
    if (section.kind === "logs") {
      return this._renderLogsSection(section);
    }
    if (section.kind === "about") {
      return this._renderAboutSection(section);
    }

    const sectionFields = section.fields || [];
    const basicFields = sectionFields.filter((field) => !field.advanced);
    const advancedFields = sectionFields.filter((field) => field.advanced);
    const scriptFields = basicFields.filter((field) => (
      field.key === "default_pre_script_key" || field.key === "default_post_script_key"
    ));
    const visibleBasicFields = basicFields.filter((field) => (
      field.key !== "default_pre_script_shared_key"
      && field.key !== "default_post_script_shared_key"
      && field.key !== "default_pre_script_say_url_key"
      && field.key !== "default_post_script_say_url_key"
    ));
    const isAdvancedOpen = this._isAdvancedOpen(section);
    const sectionDirty = this._isSectionDirty(section);
    const expanded = this._isConfigSectionExpanded(section.key);
    return `
      <section
        class="section config-section-card ${expanded ? "expanded" : "collapsed"}"
        data-section-key="${this._escapeAttribute(section.key)}"
        data-config-section-card="${this._escapeAttribute(section.key)}"
      >
        <div class="section-header">
          <div class="section-header-copy">
            <div>
              <h2>${this._escapeHtml(section.title)}</h2>
              <p>${this._escapeHtml(section.description || "")}</p>
            </div>
            ${sectionDirty ? `
              <div class="section-header-copy-actions">
                <button
                  class="button-secondary"
                  type="button"
                  data-reset-section="${this._escapeAttribute(section.key)}"
                >${this._escapeHtml(this._t("action.reset_section"))}</button>
              </div>
            ` : ""}
          </div>
          <div class="section-header-actions">
            <button
              class="button-secondary icon-only-button config-section-toggle ${expanded ? "expanded" : "collapsed"}"
              type="button"
              data-toggle-config-section="${this._escapeAttribute(section.key)}"
              aria-label="${this._escapeAttribute(this._t(expanded ? "aria.collapse_section" : "aria.expand_section"))}"
              title="${this._escapeAttribute(this._t(expanded ? "action.collapse" : "action.expand"))}"
            >${ICONS.chevron}</button>
          </div>
        </div>
        <div class="row-collapse ${expanded ? "expanded" : "collapsed"}">
          <div class="row-collapse-inner">
            <div class="config-section-body">
              <div class="field-grid">
                ${visibleBasicFields.map((field) => {
                  if (!scriptFields.includes(field)) {
                    return this._renderField(field, values[field.key], errors[field.key]);
                  }
                  const sharedKey = field.key === "default_pre_script_key"
                    ? "default_pre_script_shared_key"
                    : "default_post_script_shared_key";
                  const sharedScriptsField = basicFields.find((item) => item.key === sharedKey);
                  return this._renderScriptField(
                    field,
                    values,
                    errors[field.key],
                    values[sharedKey] !== false,
                    sharedScriptsField,
                  );
                }).join("")}
              </div>
              ${advancedFields.length > 0 ? `
                <div class="advanced-toggle-row">
                  <button class="advanced-toggle" type="button" data-toggle-advanced="${this._escapeAttribute(section.key)}">
                    ${this._escapeHtml(this._t(isAdvancedOpen ? "action.hide_advanced" : "action.show_advanced"))}
                  </button>
                </div>
                <div class="row-collapse ${isAdvancedOpen ? "expanded" : "collapsed"}">
                  <div class="row-collapse-inner">
                    <div class="field-grid advanced-fields">
                      ${advancedFields.map((field) => this._renderField(field, values[field.key], errors[field.key])).join("")}
                    </div>
                  </div>
                </div>
              ` : ""}
            </div>
          </div>
        </div>
      </section>
    `;
  }

  _renderRandomChimeSetsSection(section, error) {
    const sets = Array.isArray(this._draftValues?.chime_sets)
      ? this._draftValues.chime_sets
      : [];
    const available = Array.isArray(section.available_chimes) ? section.available_chimes : [];
    const expanded = this._isChapterExpanded("chime_sets");
    const sectionDirty = this._isFieldChanged("chime_sets");
    const restartRequired = this._randomChimeSetStructureChanged();
    const hasUnsavedSet = this._hasUnsavedRandomChimeSet();
    return `
      <div class="chapter-group chapter-workspace chime-sets-workspace ${expanded ? "expanded" : "collapsed"}" data-chapter-key="chime_sets">
        ${this._renderChapterHero({
          chapterKey: "chime_sets",
          expanded,
          title: section.title,
          description: section.description || "",
          docsUrl: section.docs_url,
          showToggleButton: true,
          bodyMarkup: `<div class="chapter-content chapter-body config-section-body">
            <div class="notify-profile-list-actions">
              <button class="button-primary" type="button" data-add-random-chime-set="1" ${hasUnsavedSet ? "disabled" : ""}>+ Add Set</button>
              ${sectionDirty ? `<button class="button-secondary" type="button" data-reset-section="${this._escapeAttribute(section.key)}">${this._escapeHtml(this._t("action.reset_section"))}</button>` : ""}
            </div>
            ${restartRequired ? '<div class="field-note">ℹ️ <strong>Restart Required</strong><br />Adding or removing a Chime Set takes effect after Home Assistant restarts. Changing selected chimes does not require a restart.</div>' : ""}
            ${error ? `<div class="error-text">${this._escapeHtml(this._formatError(error))}</div>` : ""}
            ${sets.length === 0
              ? this._renderEmptyChimeSetsIllustration()
              : sets.map((chimeSet, index) => this._renderRandomChimeSetCard(chimeSet, index, available)).join("")}
          </div>`,
        })}
      </div>
    `;
  }

  _renderEmptyChimeSetsIllustration() {
    return renderEmptyChimeSetSlotMachine(
      this._emptyChimeSetSelection,
      this._emptyChimeSetNextSelection,
    );
  }

  _randomEmptyChimeSetSelection(excludeSelection) {
    const currentSelection = Number(excludeSelection) % 3;
    return (currentSelection + 1 + Math.floor(Math.random() * 2)) % 3;
  }

  _scheduleEmptyChimeSetReelSpin() {
    if (this._emptyChimeSetSpinTimer !== null) {
      return;
    }
    this._emptyChimeSetSpinTimer = window.setTimeout(() => {
      this._emptyChimeSetSpinTimer = null;
      const chimeSets = this._draftValues?.chime_sets;
      if (Array.isArray(chimeSets) && chimeSets.length === 0) {
        this._emptyChimeSetSelection = this._emptyChimeSetNextSelection;
        this._emptyChimeSetNextSelection = this._randomEmptyChimeSetSelection(
          this._emptyChimeSetSelection,
        );
        this._render();
      }
      this._scheduleEmptyChimeSetReelSpin();
    }, 2970);
  }

  _clearEmptyChimeSetReelSpinTimer() {
    if (this._emptyChimeSetSpinTimer === null) {
      return;
    }
    window.clearTimeout(this._emptyChimeSetSpinTimer);
    this._emptyChimeSetSpinTimer = null;
  }

  _renderLegacyEmptyChimeSetsIllustration() {
    const chimeIcons = ["bell", "note", "waves"];
    const selectedIndex = this._emptyChimeSetSelection % chimeIcons.length;
    const stripIcons = Array.from({ length: 31 }, (_, index) => {
      const offset = index - 15;
      return chimeIcons[(selectedIndex + offset + 12 + chimeIcons.length) % chimeIcons.length];
    });
    const strip = stripIcons.map((icon, index) =>
      `<g transform="translate(0 ${(index - 15) * 70})">${this._renderEmptyChimeIcon(icon)}</g>`,
    ).join("");
    return `
      <div class="chime-sets-empty-state">
        <div class="chime-slot-machine">
          <svg viewBox="0 0 300 270" role="img" aria-label="An animated single-reel chime slot machine" xmlns="http://www.w3.org/2000/svg">
            <defs><linearGradient id="slot-gold" x1="0" x2="1"><stop stop-color="#b96900"/><stop offset=".42" stop-color="#ffd36a"/><stop offset="1" stop-color="#bd7308"/></linearGradient><linearGradient id="slot-pink" x1="0" x2="0" y2="1"><stop stop-color="#e90061"/><stop offset="1" stop-color="#a90050"/></linearGradient><clipPath id="chime-slot-window"><rect x="84" y="63" width="117" height="75" rx="13" /></clipPath></defs>
            <path d="M61 43h166v24H61z" fill="url(#slot-gold)" stroke="#9a5100" stroke-width="4"/><path d="M68 28h152v15H68z" fill="#e90061" stroke="#a90050" stroke-width="4"/>
            <g fill="#ffe15c">${[80, 102, 124, 146, 168, 190, 212].map((cx) => `<circle cx="${cx}" cy="35" r="3"/>`).join("")}</g>
            <path d="M57 68c0-17 14-29 31-29h110c17 0 31 12 31 29v65c0 13-10 23-23 23H80c-13 0-23-10-23-23Z" fill="url(#slot-gold)" stroke="#9a5100" stroke-width="5"/>
            <path d="M79 61h126v82H79z" fill="#fff8fa" stroke="#d7c5ca" stroke-width="4"/><rect x="84" y="63" width="117" height="75" rx="13" fill="#fff"/>
            <g clip-path="url(#chime-slot-window)"><g class="slot-reel-strip">${strip}</g></g>
            <path d="M62 151h164v72H62z" fill="url(#slot-pink)" stroke="#9e0050" stroke-width="5"/><path d="M72 170h143v43H72z" fill="none" stroke="#ffc43d" stroke-width="4"/>
            <g fill="#ffe15c">${[78, 96, 114, 132, 150, 168, 186, 204].map((cx) => `<circle cx="${cx}" cy="161" r="3"/>`).join("")}</g>
            <g class="slot-handle"><path d="M226 112 248 57" fill="none" stroke="#873c00" stroke-width="8" stroke-linecap="round"/><path d="M226 112 248 57" fill="none" stroke="#ffc64e" stroke-width="4" stroke-linecap="round"/><circle cx="251" cy="50" r="12" fill="#d90055" stroke="#9e0050" stroke-width="4"/></g>
          </svg>
        </div>
        <blockquote class="chime-slot-message">“Move the washing to the dryer”</blockquote>
      </div>
    `;
  }

  _renderEmptyChimeIcon(icon) {
    if (icon === "bell") return '<path d="M142 82c-12 0-21 10-21 22v14l-7 9h56l-7-9v-14c0-12-9-22-21-22Z" fill="#ffd83d" stroke="#153f71" stroke-width="5" stroke-linejoin="round"/><path d="M134 130c2 8 14 8 16 0" fill="none" stroke="#153f71" stroke-width="5" stroke-linecap="round"/>';
    if (icon === "note") return '<path d="M153 84v34c-4-4-15-3-19 4-5 10 6 16 15 11 5-3 6-8 6-13v-21l22-5v26c-4-4-15-3-19 4-5 10 6 16 15 11 5-3 6-8 6-13V87l-25 6Z" fill="#4b83dc" stroke="#153f71" stroke-width="5" stroke-linejoin="round"/>';
    return '<path d="M118 105v10m12-20v30m12-37v44m12-37v30m12-20v10" fill="none" stroke="#4b83dc" stroke-width="7" stroke-linecap="round"/>';
  }

  _renderRandomChimeSetCard(chimeSet, index, available) {
    const expanded = this._isRandomChimeSetExpanded(index);
    const name = String(chimeSet?.name || "").trim() || "Chime Set";
    const selectedCount = Array.isArray(chimeSet?.chimes) ? chimeSet.chimes.length : 0;
    return `
      <article class="notify-profile-card random-chime-set-card ${expanded ? "expanded" : "collapsed"}" data-random-chime-set-card="${index}" aria-expanded="${expanded ? "true" : "false"}">
        <div class="notify-profile-header random-chime-set-header" data-random-chime-set-header="${index}">
          <div class="notify-profile-copy">
            <button class="random-chime-set-row-toggle" type="button" data-toggle-random-chime-set="${index}" aria-expanded="${expanded ? "true" : "false"}"><div class="notify-profile-title-display"><h3><span class="random-chime-set-title-name">${this._escapeHtml(name)}</span><span class="random-chime-set-title-count"> - ${this._escapeHtml(`${selectedCount} ${selectedCount === 1 ? "chime" : "chimes"} selected`)}</span></h3></div></button>
            <div class="notify-profile-title-edit"><input class="notify-profile-title-input random-chime-set-title-input" data-random-set-name="${index}" type="text" value="${this._escapeAttribute(chimeSet.name || "")}" placeholder="Chime set name" /></div>
          </div>
          <div class="notify-profile-actions">
            <button class="button-danger icon-only-button" type="button" data-delete-random-chime-set="${index}" aria-label="${this._escapeAttribute(this._t("action.delete"))}" title="${this._escapeAttribute(this._t("action.delete"))}">${ICONS.trash}</button>
            <button class="button-secondary icon-only-button log-event-toggle ${expanded ? "expanded" : "collapsed"}" type="button" data-toggle-random-chime-set="${index}" aria-label="${this._escapeAttribute(this._t(expanded ? "aria.collapse_profile" : "aria.expand_profile"))}" title="${this._escapeAttribute(this._t(expanded ? "action.collapse" : "action.expand"))}">${ICONS.chevron}</button>
          </div>
        </div>
        <div class="row-collapse ${expanded ? "expanded" : "collapsed"}"><div class="row-collapse-inner">
          <div class="random-chime-member-grid chime-set-member-grid">
            ${available.map((option) => {
              const value = String(option.value || "");
              const checked = Array.isArray(chimeSet.chimes) && chimeSet.chimes.includes(value);
              const previewKey = this._getFieldPreviewKey("chime_path", value);
              const loading = this._fieldPreviewLoadingKey === previewKey;
              const playing = this._fieldPreviewPlayingKey === previewKey;
              return `<div class="random-chime-member"><label><input type="checkbox" data-random-set-member="${index}" value="${this._escapeAttribute(value)}" ${checked ? "checked" : ""} /><span>${this._escapeHtml(option.label || value)}</span></label><button class="button-secondary icon-only-button field-preview-button ${playing ? "preview-playing" : ""}" ${this._previewPlayingStyle(playing, this._fieldPreviewDuration)} type="button" data-random-chime-audio-toggle="${this._escapeAttribute(value)}" aria-label="${this._escapeAttribute(this._t(playing ? "action.pause_preview" : loading ? "action.loading_preview" : "action.play_preview"))}" title="${this._escapeAttribute(this._t(playing ? "action.pause_preview" : loading ? "action.loading_preview" : "action.play_preview"))}">${playing ? ICONS.pause : loading ? '<span class="button-spinner" aria-hidden="true"></span>' : ICONS.play}</button></div>`;
            }).join("")}
          </div>
        </div></div>
      </article>
    `;
  }

  _renderChimesSection(section, values, errors) {
    const expanded = this._isChapterExpanded("chimes");
    const folderSection = section.folder_section;
    const chimes = Array.isArray(section.available_chimes) ? section.available_chimes : [];
    const listExpanded = this._isConfigSectionExpanded("chime_list");
    return `
      <div class="chapter-group chapter-workspace chimes-workspace ${expanded ? "expanded" : "collapsed"}" data-chapter-key="chimes">
        ${this._renderChapterHero({
          chapterKey: "chimes",
          expanded,
          title: section.title,
          description: section.description || "",
          docsUrl: section.docs_url,
          bodyMarkup: `<div class="chapter-content">
            ${folderSection ? this._renderSection(folderSection, values, errors) : ""}
            <section class="section config-section chime-list-section ${listExpanded ? "expanded" : "collapsed"}" data-config-section-card="chime_list">
              <div class="section-header">
                <div>
                  <h2>Chime List</h2>
                  <p>Preview chimes and configure their offset values.</p>
                </div>
                <button class="button-secondary config-section-toggle ${listExpanded ? "expanded" : "collapsed"}" type="button" data-toggle-config-section="chime_list" aria-label="${this._escapeAttribute(this._t(listExpanded ? "action.collapse" : "action.expand"))}" title="${this._escapeAttribute(this._t(listExpanded ? "action.collapse" : "action.expand"))}">${ICONS.chevron}</button>
              </div>
              <div class="row-collapse ${listExpanded ? "expanded" : "collapsed"}"><div class="row-collapse-inner">
                <div class="random-chime-member-grid chime-list-grid">
                  ${chimes.map((option) => {
                    const value = String(option.value || "");
                    const previewKey = this._getFieldPreviewKey("chime_path", value);
                    const loading = this._fieldPreviewLoadingKey === previewKey;
                    const playing = this._fieldPreviewPlayingKey === previewKey;
                    return `<div class="random-chime-member chime-list-member"><span>${this._escapeHtml(option.label || value)}</span><button class="button-secondary icon-only-button field-preview-button ${playing ? "preview-playing" : ""}" ${this._previewPlayingStyle(playing, this._fieldPreviewDuration)} type="button" data-random-chime-audio-toggle="${this._escapeAttribute(value)}" aria-label="${this._escapeAttribute(this._t(playing ? "action.pause_preview" : loading ? "action.loading_preview" : "action.play_preview"))}" title="${this._escapeAttribute(this._t(playing ? "action.pause_preview" : loading ? "action.loading_preview" : "action.play_preview"))}">${playing ? ICONS.pause : loading ? '<span class="button-spinner" aria-hidden="true"></span>' : ICONS.play}</button><button class="button-secondary icon-only-button chime-set-offset-button" type="button" data-edit-chime-offset="${this._escapeAttribute(value)}" data-chime-offset-label="${this._escapeAttribute(option.label || value)}" aria-label="Edit chime offset" title="Edit offset">${ICONS.pencil}</button></div>`;
                  }).join("")}
                </div>
              </div></div>
            </section>
          </div>`,
        })}
      </div>
    `;
  }

  _renderSettingsContent(sections, values, errors, data) {
    const notifySection = sections.find((section) => section.kind === "notify_profiles");
    const logsSection = sections.find((section) => section.kind === "logs");
    const aboutSection = sections.find((section) => section.kind === "about");
    const chimesSection = sections.find((section) => section.kind === "chimes");
    const chimeSetsSection = sections.find((section) => section.kind === "chime_sets");
    const configSections = sections.filter((section) => !["chimes", "chime_sets", "notify_profiles", "logs", "about"].includes(section.kind));
    const configExpanded = this._isChapterExpanded("configuration");

    return `
      <div
        class="chapter-group chapter-workspace configuration-workspace ${configExpanded ? "expanded" : "collapsed"}"
        data-chapter-key="configuration"
      >
        ${this._renderChapterHero({
          chapterKey: "configuration",
          expanded: configExpanded,
          title: this._t("chapter.configuration"),
          description: this._t("chapter.configuration_description"),
          docsUrl: data.documentation_url,
          bodyMarkup: `
            <div class="chapter-content">
              ${configSections.map((section) => this._renderSection(section, values, errors)).join("")}
            </div>
          `,
        })}
      </div>
      ${chimesSection ? this._renderChimesSection(chimesSection, values, errors) : ""}
      ${chimeSetsSection ? this._renderRandomChimeSetsSection(chimeSetsSection, errors[chimeSetsSection.key]) : ""}
      ${notifySection ? this._renderNotifyProfilesSection(notifySection) : ""}
      ${logsSection ? this._renderLogsSection(logsSection) : ""}
      ${aboutSection ? this._renderAboutSection(aboutSection) : ""}
    `;
  }

  _documentationUrl(url) {
    if (!url) {
      return url;
    }
    try {
      const documentationUrl = new URL(url, window.location.origin);
      documentationUrl.searchParams.set("theme", this._hass?.themes?.darkMode ? "dark" : "light");
      return documentationUrl.toString();
    } catch (_error) {
      return url;
    }
  }

  _renderChapterHero({ chapterKey, expanded, title, description, docsUrl, actionsMarkup = "", bodyMarkup = "", showToggleButton = false }) {
    return `
      <section
        class="chapter-hero"
      >
        <div
          class="chapter-hero-toggle"
          data-toggle-chapter="${this._escapeAttribute(chapterKey)}"
          role="button"
          tabindex="0"
          aria-expanded="${expanded ? "true" : "false"}"
          aria-label="${this._escapeAttribute(this._t(expanded ? "aria.collapse_named" : "aria.expand_named", { title }))}"
        >
          <div class="chapter-hero-inner">
            <div>
              <div class="chapter-hero-copy">
                <div class="chapter-hero-title-row">
                  ${CHAPTER_ICONS[chapterKey] ? `<span class="chapter-hero-icon">${CHAPTER_ICONS[chapterKey]}</span>` : ""}
                  <h2 class="chapter-hero-title">${this._escapeHtml(title)}</h2>
                  ${docsUrl
                    ? `<a
                        class="field-help-link"
                        href="${this._escapeAttribute(this._documentationUrl(docsUrl))}"
                        target="_blank"
                        rel="noreferrer"
                        aria-label="${this._escapeAttribute(this._t("aria.open_help", { title }))}"
                        title="${this._escapeAttribute(this._t("aria.open_help", { title }))}"
                      >?</a>`
                    : ""
                  }
                </div>
                ${description ? `<p class="chapter-hero-description">${this._escapeHtml(description)}</p>` : ""}
              </div>
            </div>
            <div class="chapter-hero-endcap">
              ${expanded && actionsMarkup
                ? `<div class="chapter-hero-actions">${actionsMarkup}</div>`
                : ""
              }
              ${showToggleButton
                ? `<button class="button-secondary icon-only-button config-section-toggle chime-sets-chapter-toggle ${expanded ? "expanded" : "collapsed"}" type="button" data-toggle-chapter="${this._escapeAttribute(chapterKey)}" aria-label="${this._escapeAttribute(this._t(expanded ? "aria.collapse_named" : "aria.expand_named", { title }))}" title="${this._escapeAttribute(this._t(expanded ? "action.collapse" : "action.expand"))}">${ICONS.chevron}</button>`
                : `<span class="chapter-chevron" aria-hidden="true">${ICONS.chevron}</span>`
              }
            </div>
          </div>
        </div>
        <div class="chapter-collapse ${expanded ? "expanded" : "collapsed"}">
          <div class="chapter-collapse-inner">
            ${bodyMarkup}
          </div>
        </div>
      </section>
    `;
  }

  _renderNotifyProfilesSection(section) {
    const profiles = this._draftNotifyProfiles || [];
    const sectionDirty = this._isSectionDirty(section);
    const notifyExpanded = this._isChapterExpanded("notify_profiles");
    const notifyProfilesHydrated = this._data?.notify_profiles_hydrated !== false;
    const notifyProfilesPending = !notifyProfilesHydrated;
    const sectionTitle = section.title_key ? this._t(section.title_key) : section.title;
    const sectionDescription = section.description_key ? this._t(section.description_key) : (section.description || "");
    return `
      <div
        class="chapter-group chapter-workspace notify-workspace ${notifyExpanded ? "expanded" : "collapsed"}"
        data-chapter-key="notify_profiles"
      >
        ${this._renderChapterHero({
          chapterKey: "notify_profiles",
          expanded: notifyExpanded,
          title: sectionTitle,
          description: sectionDescription,
          docsUrl: section.docs_url,
          bodyMarkup: `
            <div class="chapter-content chapter-body">
                <div class="notify-profile-list-actions">
                  <button class="button-primary" type="button" data-add-notify-profile="1">${this._escapeHtml(this._t("action.add_profile"))}</button>
                  ${sectionDirty ? `
                    <button
                      class="button-secondary"
                      type="button"
                      data-reset-section="${this._escapeAttribute(section.key)}"
                    >${this._escapeHtml(this._t("action.reset_section"))}</button>
                  ` : ""}
                </div>
                ${notifyProfilesPending
                  ? `<p class="hint">${this._escapeHtml(this._t("loading.profiles"))}</p>`
                  : profiles.length === 0
                  ? `<p class="hint">${this._escapeHtml(this._t("empty.profiles"))}</p>`
                  : `
                    <div class="notify-profile-list">
                      ${profiles.map((profile, index) => this._renderNotifyProfileCard(section, profile, index)).join("")}
                    </div>
                  `
                }
            </div>
          `,
        })}
      </div>
    `;
  }

  _renderLogsSection(section) {
    const logsExpanded = this._isChapterExpanded("logs");
    const events = [...(this._data?.log_events || [])].reverse();
    const anyExpanded = events.some((event) => this._isLogEventExpanded(event.id));
    const logsPending = !this._logsHydrated && (this._logsOpeningRefresh || this._logsRefreshInFlight);
    const sectionTitle = section.title_key ? this._t(section.title_key) : section.title;
    const sectionDescription = section.description_key ? this._t(section.description_key) : (section.description || "");
    return `
      <div
        class="chapter-group chapter-workspace logs-workspace ${logsExpanded ? "expanded" : "collapsed"}"
        data-chapter-key="logs"
      >
        ${this._renderChapterHero({
          chapterKey: "logs",
          expanded: logsExpanded,
          title: sectionTitle,
          description: sectionDescription,
          docsUrl: section.docs_url,
          bodyMarkup: `
            <div class="chapter-content chapter-body">
                ${logsPending
                  ? `
                    <div class="logs-loading" aria-live="polite">
                      <span class="button-spinner" aria-hidden="true"></span>
                      <span>${this._escapeHtml(this._t("loading.logs"))}</span>
                    </div>
                  `
                  : ""
                }
                <div class="logs-list-actions">
                      <div class="logs-debug-control">
                        <strong>${this._escapeHtml(this._t("label.debug_logs"))}</strong>
                        <label class="control-checkbox">
                          <input type="checkbox" data-toggle-debug-logs aria-label="${this._escapeAttribute(this._t("label.debug_logs"))}" ${this._debugLogsEnabled ? "checked" : ""} ${this._debugLogsUpdating ? "disabled" : ""} />
                        </label>
                      </div>
                      <a
                        class="button-secondary"
                        href="${this._escapeAttribute(this._data?.logs_url || "/config/logs?filter=chime_tts")}"
                        title="${this._escapeAttribute(this._t("aria.open_raw_logs"))}"
                      >${this._escapeHtml(this._t("action.raw_logs"))}</a>
                      ${events.length > 1
                        ? `
                          <div class="logs-list-actions-right">
                            <button
                              class="button-secondary"
                              type="button"
                              data-toggle-all-logs="${anyExpanded ? "collapse" : "expand"}"
                            >${this._escapeHtml(this._t(anyExpanded ? "action.collapse_all" : "action.expand_all"))}</button>
                          </div>
                        `
                        : ""
                      }
                </div>
                ${this._debugLogsError ? `<p class="error-text">${this._escapeHtml(this._debugLogsError)}</p>` : ""}
                ${events.length === 0 && !logsPending
                  ? `<p class="hint">${this._escapeHtml(this._t("empty.logs"))}</p>`
                  : `
                    <div class="logs-list">
                      ${events.map((event) => this._renderLogEventRow(event)).join("")}
                    </div>
                  `}
            </div>
          `,
        })}
      </div>
    `;
  }

  _renderAboutSection(section) {
    const aboutExpanded = this._isChapterExpanded("about");
    const items = section.about_items || [];
    const sectionTitle = section.title_key ? this._t(section.title_key) : section.title;
    const sectionDescription = section.description_key ? this._t(section.description_key) : (section.description || "");
    return `
      <div
        class="chapter-group chapter-workspace about-workspace ${aboutExpanded ? "expanded" : "collapsed"}"
        data-chapter-key="about"
      >
        ${this._renderChapterHero({
          chapterKey: "about",
          expanded: aboutExpanded,
          title: sectionTitle,
          description: sectionDescription,
          docsUrl: section.docs_url,
          bodyMarkup: `
            <div class="chapter-content chapter-body">
              <div class="about-grid">
                ${items.map((item) => this._renderAboutCard(item)).join("")}
              </div>
            </div>
          `,
        })}
      </div>
    `;
  }

  _renderPageFooter(data) {
    const version = data?.version || this._data?.version || "";
    const iconUrl = data?.footer_logo_url || this._data?.footer_logo_url || "";
    const inlineMarkup =
      IS_DECEMBER
        ? CHRISTMAS_FOOTER_SVG
        : iconUrl && this._footerLogoSvgUrl === iconUrl
          ? this._footerLogoSvgMarkup
          : "";
    if (!version && !iconUrl && !inlineMarkup) {
      return "";
    }
    return `
      <div class="about-footer">
        ${inlineMarkup
          ? `<div
              class="about-logo-inline"
              data-footer-logo-play="1"
              role="button"
              tabindex="0"
              aria-label="${this._escapeAttribute(this._t("aria.play_logo_animation"))}"
            >${inlineMarkup}</div>`
          : iconUrl
          ? `<object
              class="about-logo-object"
              data="${this._escapeAttribute(iconUrl)}"
              type="image/svg+xml"
              aria-label="${this._escapeAttribute(this._t("aria.logo"))}"
            ></object>`
          : ""
        }
        ${version
          ? `<p class="about-version-line">${this._escapeHtml(this._t("label.version", { version: String(version).replace("v", "") }))}</p>`
          : ""
        }
      </div>
    `;
  }

  async _ensureFooterLogoMarkup(iconUrl) {
    const normalizedUrl = String(iconUrl || "").trim();
    if (!normalizedUrl) {
      this._footerLogoSvgMarkup = "";
      this._footerLogoSvgUrl = "";
      return;
    }
    if (this._footerLogoSvgUrl === normalizedUrl && this._footerLogoSvgMarkup) {
      return;
    }
    try {
      const response = await this._fetchPickerWithAuth(normalizedUrl);
      if (!response.ok) {
        throw new Error(`Footer logo request failed with status ${response.status}`);
      }
      const rawMarkup = await response.text();
      this._footerLogoSvgMarkup = rawMarkup
        .replace(/<\?xml[\s\S]*?\?>/gi, "")
        .replace(/<script[\s\S]*?<\/script>/gi, "")
        .replace(/\s(tabindex|role|aria-label)="[^"]*"/gi, "")
        .replace(/\sid="click-target"/gi, "")
        .trim();
      this._footerLogoSvgUrl = normalizedUrl;
    } catch (_error) {
      this._footerLogoSvgMarkup = "";
      this._footerLogoSvgUrl = normalizedUrl;
    }
  }

  _syncFooterLogoTransparency() {
    this.shadowRoot.querySelectorAll(".about-logo-object").forEach((objectElement) => {
      const applyTransparency = () => {
        try {
          const doc = objectElement.contentDocument;
          if (!doc) {
            return;
          }
          const html = doc.documentElement;
          const body = doc.body;
          const svg = doc.querySelector("svg");
          if (html) {
            html.style.background = "transparent";
            html.style.backgroundColor = "transparent";
          }
          if (body) {
            body.style.background = "transparent";
            body.style.backgroundColor = "transparent";
            body.style.margin = "0";
          }
          if (svg) {
            svg.style.background = "transparent";
            svg.style.backgroundColor = "transparent";
          }
        } catch (_error) {
          // Ignore cross-document styling failures and leave the existing asset visible.
        }
      };

      if (!objectElement.dataset.transparentBound) {
        objectElement.addEventListener("load", applyTransparency);
        objectElement.dataset.transparentBound = "1";
      }
      applyTransparency();
    });
  }

  _wireFooterLogoAnimation() {
    this.shadowRoot.querySelectorAll("[data-footer-logo-play]").forEach((container) => {
      if (container.dataset.footerLogoBound === "1") {
        return;
      }
      const playAnimation = () => {
        const svg = container.querySelector("svg");
        if (!svg) {
          return;
        }
        try {
          if (typeof svg.setCurrentTime === "function") {
            svg.setCurrentTime(0);
          }
        } catch (_error) {
          // Ignore browsers that do not expose the SVG SMIL timeline API.
        }
        container.querySelectorAll("animateTransform").forEach((node) => {
          if (typeof node.beginElement === "function") {
            try {
              node.beginElement();
            } catch (_error) {
              // Ignore animation restarts that are not supported.
            }
          }
        });
      };
      container.addEventListener("click", playAnimation);
      container.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
          return;
        }
        event.preventDefault();
        playAnimation();
      });
      container.dataset.footerLogoBound = "1";
    });
  }

  _renderAboutCard(item) {
    return `
      <article class="about-card">
        <div class="about-card-header">
          <h3 class="about-card-title">${this._escapeHtml(item.title || "")}</h3>
          ${item.value
            ? `<span class="about-card-value">${this._escapeHtml(String(item.value))}</span>`
            : ""
          }
        </div>
        ${item.description
          ? `<p class="about-card-description">${this._escapeHtml(item.description)}</p>`
          : ""
        }
        ${item.url
          ? `<a
              class="about-card-link"
              href="${this._escapeAttribute(item.url)}"
              target="_blank"
              rel="noreferrer"
            >${this._escapeHtml(item.link_label || this._t("action.open"))}</a>`
          : ""
        }
      </article>
    `;
  }

  _renderLogEventRow(event) {
    const expanded = this._isLogEventExpanded(event.id);
    const rowClass = event.has_error
      ? "error"
      : this._escapeAttribute(event.row_color || "action");
    const eventIcon = this._getLogEventIcon(event);
    const eventIconClass = this._getLogEventIconClass(event);
    const rawLogLines = (event.raw_logs || [])
      .map((entry) => `[${entry.timestamp}] ${String(entry.level || "").toUpperCase()} ${entry.logger}: ${entry.message}`);
    const rawLogs = rawLogLines.join("\n");
    const rawLogsMarkup = rawLogLines.length > 0
      ? rawLogLines
        .map((line) => {
          const normalized = String(line).toUpperCase();
          let severityClass = "";
          if (normalized.includes("] ERROR ")) {
            severityClass = " error";
          } else if (normalized.includes("] WARNING ")) {
            severityClass = " warning";
          }
          return `<span class="log-event-raw-line${severityClass}">${this._escapeHtml(line)}</span>`;
        })
        .join("")
      : this._escapeHtml(this._t("empty.raw_logs"));
    const logCopyState = this._getLogCopyState(event.id);
    const logEventBody = expanded
      ? `
        <div class="log-event-body">
          ${event.summary
            ? `<p class="log-event-summary">${this._escapeHtml(event.summary)}</p>`
            : ""
          }
          <pre class="log-event-raw">${rawLogsMarkup}</pre>
        </div>
      `
      : "";
    const buttons = [];
    if (rawLogs) {
      buttons.push(`
        <button class="button-secondary" type="button" data-copy-log-raw="${this._escapeAttribute(event.id)}">${logCopyState.logs ? `<span class="copied-label">${ICONS.check}<span>${this._escapeHtml(this._t("status.copied"))}</span></span>` : this._escapeHtml(this._t("action.copy_logs"))}</button>
      `);
    }
    if (event.copy_yaml) {
      buttons.push(`
        <button class="button-secondary" type="button" data-copy-log-yaml="${this._escapeAttribute(event.id)}">${logCopyState.yaml ? `<span class="copied-label">${ICONS.check}<span>${this._escapeHtml(this._t("status.copied"))}</span></span>` : this._escapeHtml(this._t("action.copy_yaml"))}</button>
      `);
    }
    if (event.can_repeat) {
      buttons.push(`
        <button class="button-primary" type="button" data-repeat-log-action="${this._escapeAttribute(event.id)}">${this._escapeHtml(this._t("action.repeat"))}</button>
      `);
    }
    return `
      <article
        class="log-event-row ${rowClass}"
        data-log-event-id="${this._escapeAttribute(event.id)}"
        data-toggle-log-event="${this._escapeAttribute(event.id)}"
        role="button"
        tabindex="0"
        aria-expanded="${expanded ? "true" : "false"}"
      >
        <div class="log-event-row-header">
          <div class="log-event-row-content">
            <div class="log-event-row-main">
              ${eventIcon ? `<span class="log-event-icon ${this._escapeAttribute(eventIconClass)}" aria-hidden="true">${eventIcon}</span>` : ""}
              <div class="log-event-copy">
                <p class="log-event-title">${this._escapeHtml(event.title || this._t("label.log_event"))}</p>
                <p class="log-event-meta">${this._escapeHtml(this._formatLogEventMeta(event))}</p>
              </div>
            </div>
            ${buttons.length > 0 ? `<div class="log-event-actions">${buttons.join("")}</div>` : ""}
          </div>
          <div class="log-event-toggle-wrap">
            <button
              class="button-secondary log-event-toggle ${expanded ? "expanded" : "collapsed"}"
              type="button"
              data-toggle-log-arrow="${this._escapeAttribute(event.id)}"
              aria-label="${this._escapeAttribute(this._t(expanded ? "aria.collapse_log" : "aria.expand_log"))}"
              title="${this._escapeAttribute(this._t(expanded ? "action.collapse" : "action.expand"))}"
            >${ICONS.chevron}</button>
          </div>
        </div>
        <div class="row-collapse ${expanded ? "expanded" : "collapsed"}">
          <div class="row-collapse-inner">
            ${logEventBody}
          </div>
        </div>
      </article>
    `;
  }

  _renderNotifyProfileCard(section, profile, index) {
    const schemaFields = section.profile_fields || [];
    const errors = this._getNotifyProfileErrors(index);
    const validationMessages = [];
    if (errors?.name) {
      validationMessages.push("Enter a profile name.");
    }
    if (errors?.targets || errors?.entity_id) {
      validationMessages.push("Select at least one target.");
    }
    const hasValidationErrors = validationMessages.length > 0;
    const expanded = this._isNotifyProfileExpanded(index);
    const testState = this._getNotifyProfileTestState(index);
    const hasUnsavedChanges = this._isNotifyProfileDirty(index);
    const name = String(profile?.name || "").trim() || this._t("label.profile", { number: index + 1 });
    const detailFields = schemaFields.filter((field) => !["name", "entity_id"].includes(field.key));
    const boolFields = detailFields.filter((field) => field.type === "boolean");
    const standardFields = detailFields.filter((field) => field.type !== "boolean");
    const notifyProfileBody = expanded
      ? `
        <div class="notify-profile-grid compact">
          ${this._renderNotifyEntityPicker(profile, errors, index)}
          ${standardFields.map((field) => this._renderNotifyProfileField(field, profile?.[field.key], errors?.[field.key], index)).join("")}
        </div>
        ${boolFields.length > 0
          ? `
            <div class="notify-profile-flags">
              ${boolFields.map((field) => this._renderNotifyProfileField(field, profile?.[field.key], errors?.[field.key], index)).join("")}
            </div>
          `
          : ""
        }
      `
      : "";

    return `
      <article
        class="notify-profile-card ${expanded ? "expanded" : "collapsed"} ${hasValidationErrors ? "error" : ""}"
        data-notify-profile-card="${this._escapeAttribute(String(index))}"
        role="button"
        tabindex="0"
        aria-expanded="${expanded ? "true" : "false"}"
      >
        <div class="notify-profile-header">
          <div class="notify-profile-copy ${testState.open ? "testing" : ""}">
            ${testState.open
              ? ""
              : `
                <div class="notify-profile-title-display">
                  <h3>${this._escapeHtml(name)}</h3>
                </div>
                <div class="notify-profile-title-edit">
                  <input
                    class="notify-profile-title-input ${errors?.name ? "error" : ""}"
                    data-notify-field="name"
                    data-notify-index="${this._escapeAttribute(String(index))}"
                    type="text"
                    value="${this._escapeAttribute(String(profile?.name ?? ""))}"
                    placeholder="${this._escapeAttribute(this._t("placeholder.service_name"))}"
                    ${errors?.name ? 'aria-invalid="true"' : ""}
                  />
                </div>
              `
            }
          </div>
          <div class="notify-profile-actions ${testState.open ? "testing" : ""}">
            ${testState.open
              ? `
                <input
                  class="control notify-inline-test-input"
                  data-notify-inline-test-message="1"
                  data-notify-index="${this._escapeAttribute(String(index))}"
                  type="text"
                  value="${this._escapeAttribute(testState.message)}"
                  placeholder="${this._escapeAttribute(this._t("placeholder.tts_text"))}"
                />
                ${testState.sent
                  ? `<span class="save-status success notify-inline-test-sent" aria-live="polite">&#10003; ${this._escapeHtml(this._t("status.sent"))}</span>`
                  : `
                    <button
                      class="button-primary"
                      type="button"
                      data-run-notify-inline-test="${this._escapeAttribute(String(index))}"
                      ${testState.sending || hasUnsavedChanges || !String(testState.message || "").trim() ? "disabled" : ""}
                    >
                      ${testState.sending
                        ? '<span class="button-spinner" aria-hidden="true"></span>'
                        : this._escapeHtml(this._t("action.send"))
                      }
                    </button>
                  `
                }
                <button
                  class="button-secondary"
                  type="button"
                  data-close-notify-test="${this._escapeAttribute(String(index))}"
                  aria-label="${this._escapeAttribute(this._t("aria.close_test"))}"
                  title="${this._escapeAttribute(this._t("action.close"))}"
                >X</button>
              `
              : `
                ${hasUnsavedChanges
                  ? `<button class="button-secondary" type="button" data-reset-notify-profile="${this._escapeAttribute(String(index))}">${this._escapeHtml(this._t("action.reset"))}</button>`
                  : `<button
                      class="button-secondary"
                      type="button"
                      data-open-notify-test="${this._escapeAttribute(String(index))}"
                      aria-label="Run"
                      title="Run"
                    >${ICONS.play}<span>Run</span></button>`
                }
                <button
                  class="button-danger icon-only-button"
                  type="button"
                  data-remove-notify-profile="${this._escapeAttribute(String(index))}"
                  aria-label="${this._escapeAttribute(this._t("aria.delete_profile"))}"
                  title="${this._escapeAttribute(this._t("action.delete"))}"
                >${ICONS.trash}</button>
                <button
                  class="button-secondary icon-only-button log-event-toggle ${expanded ? "expanded" : "collapsed"}"
                  type="button"
                  data-toggle-notify-profile="${this._escapeAttribute(String(index))}"
                  aria-label="${this._escapeAttribute(this._t(expanded ? "aria.collapse_profile" : "aria.expand_profile"))}"
                  title="${this._escapeAttribute(this._t(expanded ? "action.collapse" : "action.expand"))}"
                >${ICONS.chevron}</button>
              `
            }
          </div>
        </div>
        ${hasValidationErrors
          ? `<p class="notify-profile-validation-error" role="alert">Cannot save this profile: ${this._escapeHtml(validationMessages.join(" "))}</p>`
          : ""
        }
        <div class="row-collapse ${expanded ? "expanded" : "collapsed"}">
          <div class="row-collapse-inner">
            ${notifyProfileBody}
          </div>
        </div>
      </article>
    `;
  }

  _renderNotifyEntityPicker(profile, errors, index) {
    const selectedEntities = this._notifyTargets(profile);
    const entityField = this._findNotifyProfileField("entity_id");
    const helpLink = entityField?.docs_url
      ? `<a
          class="field-help-link"
          href="${this._escapeAttribute(this._documentationUrl(entityField.docs_url))}"
          target="_blank"
          rel="noreferrer"
          aria-label="${this._escapeAttribute(this._t("aria.open_help", { title: entityField.label }))}"
          title="${this._escapeAttribute(this._t("aria.open_help", { title: entityField.label }))}"
        >?</a>`
      : "";
    return `
      <div class="field wide ${errors?.targets || errors?.entity_id ? "error" : ""}">
        <div class="field-top">
          <div class="field-header">
            <div class="field-copy">
              <div class="field-label-row">
                <p class="field-label">${this._escapeHtml(this._t("label.target_media_players"))}</p>
                ${helpLink}
              </div>
            </div>
          </div>
          <span class="required">${this._escapeHtml(this._t("label.required"))}</span>
          <div class="field-description-row">
            <p class="field-description">${this._escapeHtml(this._t("description.target_media_players"))}</p>
          </div>
        </div>
        ${selectedEntities.length > 0
          ? `
            <div class="notify-entity-chip-list">
              ${selectedEntities.map((target) => `
                <button
                  class="notify-entity-chip"
                  type="button"
                  data-notify-index="${this._escapeAttribute(String(index))}"
                  data-remove-notify-entity="${this._escapeAttribute(`${target.type}:${target.id}`)}"
                >
                  <span>${this._escapeHtml(`${this._notifyTargetLabel(target.type)}: ${target.id}`)}</span>
                  <span aria-hidden="true">×</span>
                </button>
              `).join("")}
            </div>
          `
          : `<p class="hint">${this._escapeHtml(this._t("empty.media_players"))}</p>`
        }
        <ha-selector class="notify-target-picker" data-notify-target-picker="${this._escapeAttribute(String(index))}"></ha-selector>
        <div class="error-text">${errors?.targets || errors?.entity_id ? this._escapeHtml(this._formatError(errors?.targets || errors?.entity_id)) : ""}</div>
      </div>
    `;
  }

  _renderNotifyProfileField(field, value, error, index) {
    const classes = ["field"];
    if (field.type === "textarea" || field.key === "options") {
      classes.push("wide");
    }
    if (error) {
      classes.push("error");
    }
    const helpLink = field.docs_url
      ? `<a
          class="field-help-link"
          href="${this._escapeAttribute(this._documentationUrl(field.docs_url))}"
          target="_blank"
          rel="noreferrer"
          aria-label="${this._escapeAttribute(this._t("aria.open_help", { title: field.label }))}"
          title="${this._escapeAttribute(this._t("aria.open_help", { title: field.label }))}"
        >?</a>`
      : "";

    let control = "";
    if (field.type === "boolean") {
      control = `
        <label class="control-checkbox notify-flag-checkbox">
          <input
            data-notify-field="${this._escapeAttribute(field.key)}"
            data-notify-index="${this._escapeAttribute(String(index))}"
            type="checkbox"
            ${value ? "checked" : ""}
          />
          <span class="field-label-row">
            <span>${this._escapeHtml(field.label)}</span>
            ${helpLink}
          </span>
        </label>
      `;
    } else if (field.type === "select") {
      const selectedValue = value === null || value === undefined ? "" : String(value);
      const selectMarkup = `
        <select
          class="control-select"
          data-notify-field="${this._escapeAttribute(field.key)}"
          data-notify-index="${this._escapeAttribute(String(index))}"
        >
          ${(field.options || []).map((option) => {
            const optionValue = String(option.value ?? "");
            return `<option value="${this._escapeAttribute(optionValue)}" ${optionValue === selectedValue ? "selected" : ""}>${this._escapeHtml(option.label ?? optionValue)}</option>`;
          }).join("")}
        </select>
      `;
      if (this._isChimePreviewField(field) && selectedValue) {
        const previewKey = this._getNotifyPreviewKey(index, field.key, selectedValue);
        const isLoading = this._notifyPreviewLoadingKey === previewKey;
        const isPlaying = this._notifyPreviewPlayingKey === previewKey;
        const actionLabel = this._t(isPlaying ? "action.pause_preview" : isLoading ? "action.loading_preview" : "action.play_preview");
        control = `
          <div class="input-row select-preview-row">
            ${selectMarkup}
            <button
              class="button-secondary icon-only-button field-preview-button ${isPlaying ? "preview-playing" : ""}"
              ${this._previewPlayingStyle(isPlaying, this._notifyPreviewDuration)}
              type="button"
              data-notify-audio-toggle="${this._escapeAttribute(field.key)}"
              data-notify-audio-value="${this._escapeAttribute(selectedValue)}"
              data-notify-index="${this._escapeAttribute(String(index))}"
              aria-label="${this._escapeAttribute(`${actionLabel} for ${field.label}`)}"
              title="${this._escapeAttribute(actionLabel)}"
            >${isPlaying ? ICONS.pause : isLoading ? '<span class="button-spinner" aria-hidden="true"></span>' : ICONS.play}</button>
          </div>
        `;
      } else {
        control = selectMarkup;
      }
    } else if (field.type === "range") {
      const normalizedValue = value === null || value === undefined || value === "" ? "" : String(value);
      const minimum = Number(field.min ?? 0);
      const maximum = Number(field.max ?? 100);
      const rangeValue = Number(normalizedValue === "" ? minimum : normalizedValue);
      const rangeProgress = maximum === minimum
        ? 0
        : Math.min(100, Math.max(0, ((rangeValue - minimum) / (maximum - minimum)) * 100));
      control = `
        <div class="notify-range">
          <input
            class="control-range"
            data-notify-range="${this._escapeAttribute(field.key)}"
            data-notify-index="${this._escapeAttribute(String(index))}"
            type="range"
            min="${this._escapeAttribute(String(field.min ?? 0))}"
            max="${this._escapeAttribute(String(field.max ?? 100))}"
            step="${this._escapeAttribute(String(field.step ?? 1))}"
            value="${this._escapeAttribute(normalizedValue === "" ? String(field.min ?? 0) : normalizedValue)}"
            style="--range-progress: ${this._escapeAttribute(String(rangeProgress))}%"
          />
          <input
            class="control notify-range-number"
            data-notify-range-number="${this._escapeAttribute(field.key)}"
            data-notify-index="${this._escapeAttribute(String(index))}"
            type="number"
            min="${this._escapeAttribute(String(field.min ?? 0))}"
            max="${this._escapeAttribute(String(field.max ?? 100))}"
            step="${this._escapeAttribute(String(field.step ?? 1))}"
            value="${this._escapeAttribute(normalizedValue === "" ? "" : normalizedValue)}"
            placeholder="${this._escapeAttribute(normalizedValue === "" ? this._t("placeholder.auto", { unit: field.unit ? ` ${field.unit}` : "" }) : "")}"
          />
        </div>
      `;
    } else if (field.type === "textarea") {
      control = `
        <textarea
          class="control control-textarea"
          data-notify-field="${this._escapeAttribute(field.key)}"
          data-notify-index="${this._escapeAttribute(String(index))}"
          placeholder="${this._escapeAttribute(field.placeholder || "")}"
        >${this._escapeHtml(String(value ?? ""))}</textarea>
      `;
    } else {
      control = `
        <input
          class="control"
          data-notify-field="${this._escapeAttribute(field.key)}"
          data-notify-index="${this._escapeAttribute(String(index))}"
          type="${field.type === "number" ? "number" : "text"}"
          value="${this._escapeAttribute(String(value ?? ""))}"
          placeholder="${this._escapeAttribute(field.placeholder || "")}"
          ${field.type === "number" ? 'step="any"' : ""}
        />
      `;
    }

    const controlMarkup = control;

    return `
      <div class="${classes.join(" ")}">
        ${field.type !== "boolean"
          ? `
            <div class="field-top">
              <div class="field-header">
                <div class="field-copy">
                  <div class="field-label-row">
                    <p class="field-label">${this._escapeHtml(field.label)}</p>
                    ${helpLink}
                    ${this._isNotifyProfileFieldChanged(index, field.key)
                      ? `
                        <span class="spacer"></span>
                        <button
                          type="button"
                          class="field-reset-link"
                          data-reset-notify-field="${this._escapeAttribute(field.key)}"
                          data-notify-index="${this._escapeAttribute(String(index))}"
                        >${this._escapeHtml(this._t("action.reset"))}</button>
                      `
                      : ""
                    }
                  </div>
                </div>
              </div>
              ${field.required ? `<span class="required">${this._escapeHtml(this._t("label.required"))}</span>` : ""}
              ${field.description && field.key === "audio_conversion"
                ? `
                  <div class="field-description-row">
                    <p class="field-description">${this._escapeHtml(field.description)}</p>
                  </div>
                `
                : ""
              }
            </div>
              `
          : ""
        }
        ${controlMarkup}
        <div class="error-text">${error ? this._escapeHtml(this._formatError(error)) : ""}</div>
      </div>
    `;
  }

  _renderField(field, value, error) {
    const fieldClasses = ["field"];
    if (field.wide) {
      fieldClasses.push("wide");
    }
    if (error || this._hasBlockingPathValidationError(field, value)) {
      fieldClasses.push("error");
    }
    const isChanged = this._isFieldChanged(field.key);
    if (isChanged) {
      fieldClasses.push("changed");
    }

    const control = field.type === "boolean"
      ? this._renderBoolean(field, value)
      : field.type === "select"
        ? this._renderSelect(field, value)
        : this._renderInput(field, value);
    const fieldIconUrl = field.icon_url || (field.key && OPTION_ICON_DATA_URLS[field.key]
      ? OPTION_ICON_DATA_URLS[field.key]
      : (field.key
        ? `/api/chime_tts/images/option_icons/${field.key}.svg`
        : ""));
    const normalizedFieldIconUrl = fieldIconUrl.startsWith("data:image/svg+xml;")
      ? fieldIconUrl.replaceAll("#", "%23")
      : fieldIconUrl;
    const providerHint = this._renderFieldSubhint(this._resolveProviderHint(field));
    const emptyDefaultHint = this._renderEmptyDefaultHint(field, value);
    const livePathValidation = this._renderPathValidation(field);
    const helpLink = field.docs_url
      ? `<a
          class="field-help-link"
          href="${this._escapeAttribute(this._documentationUrl(field.docs_url))}"
          target="_blank"
          rel="noreferrer"
          aria-label="${this._escapeAttribute(this._t("aria.open_help", { title: field.label }))}"
          title="${this._escapeAttribute(this._t("aria.open_help", { title: field.label }))}"
        >?</a>`
      : "";
    return `
      <div class="${fieldClasses.join(" ")}" data-field-key="${this._escapeAttribute(field.key || "")}">
        <div class="field-top with-icon">
          <img class="field-icon" src="${this._escapeAttribute(normalizedFieldIconUrl)}" alt="" loading="lazy" />
          <div class="field-header">
            <div class="field-copy">
              <div class="field-label-row">
                <p class="field-label">${this._escapeHtml(field.label)}</p>
                ${isChanged ? `<span class="field-changed-pill">${this._escapeHtml(this._t("status.changed"))}</span>` : ""}
                ${helpLink}
              </div>
            </div>
          </div>
          ${field.required ? `<span class="required">${this._escapeHtml(this._t("label.required"))}</span>` : ""}
          <div class="field-description-row">
            <p class="field-description">${this._escapeHtml(field.description || "")}</p>
          </div>
        </div>
        ${control}
        ${providerHint}
        ${emptyDefaultHint}
        ${livePathValidation}
        <div class="error-text">${error ? this._escapeHtml(this._formatError(error)) : ""}</div>
      </div>
    `;
  }

  _renderScriptField(field, values, error, useSharedScripts, sharedScriptsField) {
    const sayUrlKey = field.key === "default_pre_script_key"
      ? "default_pre_script_say_url_key"
      : "default_post_script_say_url_key";
    const fieldClasses = ["field"];
    if (this._isFieldChanged(field.key) || this._isFieldChanged(sayUrlKey)) {
      fieldClasses.push("changed");
    }
    const helpLink = field.docs_url
      ? `<a class="field-help-link" href="${this._escapeAttribute(this._documentationUrl(field.docs_url))}" target="_blank" rel="noreferrer" aria-label="${this._escapeAttribute(this._t("aria.open_help", { title: field.label }))}" title="${this._escapeAttribute(this._t("aria.open_help", { title: field.label }))}">?</a>`
      : "";
    return `
      <div class="${fieldClasses.join(" ")}" data-field-key="${this._escapeAttribute(field.key)}">
        <div class="field-top with-icon">
          <img class="field-icon" src="${this._escapeAttribute(field.icon_url || "")}" alt="" loading="lazy" />
          <div class="field-header"><div class="field-copy"><div class="field-label-row">
            <p class="field-label">${this._escapeHtml(field.label)}</p>${helpLink}
          </div></div></div>
          <div class="field-description-row"><p class="field-description">${this._escapeHtml(field.description || "")}</p></div>
        </div>
        ${useSharedScripts ? "" : '<p class="script-action-label">chime_tts.say</p>'}
        ${this._renderInput(field, values[field.key])}
        ${useSharedScripts ? "" : `
          <p class="script-action-label">chime_tts.say_url</p>
          ${this._renderInput({ ...field, key: sayUrlKey }, values[sayUrlKey])}
        `}
        ${sharedScriptsField ? `
          <div>
            <label class="control-checkbox">
              <input
                data-field="${this._escapeAttribute(sharedScriptsField.key)}"
                type="checkbox"
                ${values[sharedScriptsField.key] ? "checked" : ""}
              />
              <span>${this._escapeHtml(sharedScriptsField.label)}</span>
            </label>
          </div>
        ` : ""}
        <div class="error-text">${error ? this._escapeHtml(this._formatError(error)) : ""}</div>
      </div>
    `;
  }

  _renderInput(field, value) {
    const type = field.type === "number" ? "number" : "text";
    const normalizedValue = value === null || value === undefined ? "" : value;
    const minAttr = field.min !== null && field.min !== undefined ? `min="${this._escapeAttribute(String(field.min))}"` : "";
    const stepAttr = type === "number" ? `step="${this._escapeAttribute(String(field.step || 1))}"` : "";
    const placeholderAttr = field.placeholder ? `placeholder="${this._escapeAttribute(String(field.placeholder))}"` : "";
    const pathValidation = field.can_browse ? this._getPathValidationState(field) : null;
    const showInvalidIndicator = Boolean(
      field.can_browse
      && pathValidation
      && pathValidation.valid === false
      && String(normalizedValue).trim() !== ""
      && !this._invalidPathOverrides?.[field.key]
    );
    const ariaInvalid = this._hasBlockingPathValidationError(field, normalizedValue)
      ? ' aria-invalid="true"'
      : "";

    const inputMarkup = field.type === "textarea"
      ? `
        <textarea
          class="control control-textarea"
          data-field="${this._escapeAttribute(field.key)}"
          ${placeholderAttr}
        >${this._escapeHtml(String(normalizedValue))}</textarea>
      `
      : `
      <input
        class="control"
        data-field="${this._escapeAttribute(field.key)}"
        type="${type}"
        value="${this._escapeAttribute(String(normalizedValue))}"
        ${minAttr}
        ${stepAttr}
        ${placeholderAttr}
        ${ariaInvalid}
      />
    `;

    if (field.type === "textarea" || type !== "text" || !field.can_browse) {
      return inputMarkup;
    }

    return `
      <div class="input-row">
        ${inputMarkup}
        ${showInvalidIndicator
          ? `<button class="path-inline-action" type="button" data-use-anyway="${this._escapeAttribute(field.key)}">${this._escapeHtml(this._t("action.use_anyway"))}</button>`
          : ""
        }
        <button class="browse-button" type="button" data-browse-field="${this._escapeAttribute(field.key)}">${this._escapeHtml(this._t("action.browse"))}</button>
      </div>
    `;
  }

  _renderSelect(field, value) {
    const selectedValue = value === null || value === undefined ? "" : String(value);
    const usesPlaceholder = Boolean(field.placeholder);
    const visibleOptions = usesPlaceholder
      ? (field.options || []).filter((option) => String(option.value ?? "") !== "")
      : (field.options || []);
    const selectMarkup = `
      <select class="control-select" data-field="${this._escapeAttribute(field.key)}">
        ${usesPlaceholder && selectedValue === ""
          ? `<option value="" selected disabled hidden>${this._escapeHtml(field.placeholder)}</option>`
          : ""
        }
        ${visibleOptions.map((option) => {
          const optionValue = String(option.value ?? "");
          const selected = optionValue === selectedValue ? "selected" : "";
          return `<option value="${this._escapeAttribute(optionValue)}" ${selected}>${this._escapeHtml(option.label ?? optionValue)}</option>`;
        }).join("")}
      </select>
    `;

    if (!this._isChimePreviewField(field) || !selectedValue) {
      return selectMarkup;
    }

    const previewKey = this._getFieldPreviewKey(field.key, selectedValue);
    const isLoading = this._fieldPreviewLoadingKey === previewKey;
    const isPlaying = this._fieldPreviewPlayingKey === previewKey;
    const actionLabel = this._t(isPlaying ? "action.pause_preview" : isLoading ? "action.loading_preview" : "action.play_preview");
    return `
      <div class="input-row select-preview-row">
        ${selectMarkup}
        <button
          class="button-secondary icon-only-button field-preview-button ${isPlaying ? "preview-playing" : ""}"
          ${this._previewPlayingStyle(isPlaying, this._fieldPreviewDuration)}
          type="button"
          data-field-audio-toggle="${this._escapeAttribute(field.key)}"
          data-field-audio-value="${this._escapeAttribute(selectedValue)}"
          aria-label="${this._escapeAttribute(`${actionLabel} for ${field.label}`)}"
          title="${this._escapeAttribute(actionLabel)}"
        >${isPlaying ? ICONS.pause : isLoading ? '<span class="button-spinner" aria-hidden="true"></span>' : ICONS.play}</button>
      </div>
    `;
  }

  _renderBoolean(field, value) {
    return `
      <label class="control-checkbox">
        <input
          data-field="${this._escapeAttribute(field.key)}"
          type="checkbox"
          ${value ? "checked" : ""}
        />
        <span>${this._escapeHtml(this._t("label.enabled"))}</span>
      </label>
    `;
  }

  _renderFieldSubhint(hint) {
    if (!hint?.message) {
      return "";
    }
    const tone = hint.tone || "info";
    return `<div class="field-subhint ${this._escapeAttribute(tone)}">${this._escapeHtml(hint.message)}</div>`;
  }

  _resolveProviderHint(field) {
    if (!field) {
      return null;
    }

    const selectedProvider = field.key === "fallback_tts_platform_key"
      ? String(this._draftValues?.fallback_tts_platform_key || "").trim()
      : String(this._draftValues?.tts_platform_key || "").trim();

    if (!selectedProvider) {
      return field.provider_hint || null;
    }

    return field.provider_hints?.[selectedProvider] || field.provider_hint || null;
  }

  _renderEmptyDefaultHint(field, value) {
    if (!field.empty_default_hint || field.required || field.type === "boolean" || field.can_browse) {
      return "";
    }

    const normalized = value === null || value === undefined ? "" : String(value).trim();
    if (normalized !== "") {
      return "";
    }

    return `<div class="field-subhint muted">${this._escapeHtml(field.empty_default_hint)}</div>`;
  }

  _renderPathValidation(field) {
    if (!field.can_browse) {
      return "";
    }

    const validation = this._getPathValidationState(field);
    if (!validation?.message) {
      return "";
    }
    if (validation.valid && String(this._draftValues?.[field.key] || "").trim() !== "") {
      return "";
    }
    const suggestionLinks = (validation.suggestion_paths || []).length > 0
      ? `
        <div class="field-subhint-links">
          ${(validation.suggestion_paths || []).map((path) => `
            <a href="#" data-set-path="${this._escapeAttribute(field.key)}" data-path-value="${this._escapeAttribute(path)}">${this._escapeHtml(path)}</a>
          `).join("")}
        </div>
      `
      : "";

    return `
      <div class="field-subhint ${this._escapeAttribute(validation.tone || "muted")}">
        ${this._escapeHtml(validation.message)}
        ${suggestionLinks}
      </div>
    `;
  }

  _renderPicker() {
    if (!this._picker) {
      return "";
    }

    const items = this._getVisiblePickerItems();
    const hasParentRow = Boolean(this._picker.parent_path);
    const roots = this._picker.roots || [];
    const capabilities = this._picker.capabilities || {};
    const loading = this._pickerLoadingVisible
      ? `<p class="picker-empty">${this._escapeHtml(this._t("loading.items"))}</p>`
      : "";
    const error = this._pickerError
      ? `<div class="message error picker-error-banner">${this._escapeHtml(this._pickerError)}</div>`
      : "";
    const notice = this._picker?.requested_path_missing && this._picker?.selected_path_notice
      ? `<div class="message warning picker-warning-banner">${this._escapeHtml(this._picker.selected_path_notice)}</div>`
      : "";
    const isEmpty = !this._pickerLoading && items.length === 0;
    const empty = isEmpty
      ? `<p class="picker-empty">${this._escapeHtml(this._t("empty.folder"))}</p>`
      : "";
    const breadcrumbs = (this._picker.breadcrumbs || []).map((segment, index) => {
      if (index === 0) {
        return `<button class="picker-breadcrumb-home" type="button" data-picker-path="${this._escapeAttribute(segment.path)}" aria-label="${this._escapeAttribute(this._t("aria.open_named", { title: segment.label }))}">${ICONS.folder}</button>`;
      }
      return `
        <span class="picker-path-separator">/</span>
        <button class="picker-path-button" type="button" data-picker-path="${this._escapeAttribute(segment.path)}">${this._escapeHtml(segment.label)}</button>
      `;
    }).join("");
    const currentPath = this._picker.current_path || "";
    const selectedPath = this._pickerSelectedPath || currentPath;
    const canSelect = Boolean(selectedPath && this._isPickerPathSelectable(selectedPath));
    const pickerTitle = this._picker.title || this._t("action.select_folder");
    const menuOpen = Boolean(this._pickerMenuOpen);
    const preview = empty ? "" : this._renderPickerPreview();
    const rootList = roots.map((root) => `
      <button
        class="picker-root ${root.path === currentPath ? "active" : ""}"
        type="button"
        data-picker-root="${this._escapeAttribute(root.path)}"
      >
        <span class="picker-root-title">${this._escapeHtml(root.name)}</span>
        <span class="picker-root-path">${this._escapeHtml(root.path)}</span>
      </button>
    `).join("");

    return `
      <div class="picker-modal-backdrop" data-picker-overlay="1">
        <div
          class="picker-modal"
          data-picker-dialog="1"
          role="dialog"
          aria-modal="true"
          aria-label="${this._escapeAttribute(pickerTitle)}"
        >
          <div class="picker-modal-header">
            <h2 class="picker-modal-title">${this._escapeHtml(pickerTitle)}</h2>
            <button
              class="button-secondary icon-only-button picker-modal-close"
              type="button"
              data-picker-close="1"
              aria-label="${this._escapeAttribute(this._t("aria.close_folder_browser"))}"
              title="${this._escapeAttribute(this._t("aria.close_folder_browser"))}"
            >${ICONS.close}</button>
          </div>
          <div class="picker-dialog-body">
          <input data-picker-file-input type="file" multiple accept="${AUDIO_FILE_ACCEPT}" hidden />
          <input data-picker-folder-input type="file" webkitdirectory directory multiple accept="${AUDIO_FILE_ACCEPT}" hidden />
          ${error}
          ${notice}
          <div class="picker-browser-shell">
            <aside class="picker-browser-sidebar">
              <div class="picker-sidebar-header">
                <p class="picker-location-label">${this._escapeHtml(this._t("label.locations"))}</p>
              </div>
              <div class="picker-sidebar-list">
                ${rootList}
              </div>
            </aside>
            <section class="picker-browser-main">
              <div class="picker-browser-toolbar">
                <div class="picker-browser-toolbar-left">
                  <input
                    class="control picker-search"
                    data-picker-filter="1"
                    type="search"
                    value="${this._escapeAttribute(this._pickerFilter || "")}"
                    placeholder="${this._escapeAttribute(this._t("placeholder.search_folder"))}"
                  />
                </div>
                <div class="picker-browser-toolbar-right">
                  <button
                    class="button-secondary icon-only-button picker-overflow-toggle"
                    type="button"
                    data-picker-menu-toggle="1"
                    aria-expanded="${menuOpen ? "true" : "false"}"
                    aria-label="${this._escapeAttribute(this._t("aria.more_actions"))}"
                    title="${this._escapeAttribute(this._t("aria.more_actions"))}"
                  >${ICONS.more}</button>
                  ${menuOpen
                    ? `
                      <div class="picker-overflow-menu">
                        <button class="button-secondary picker-overflow-item" type="button" data-picker-refresh="1">${ICONS.refresh}<span>${this._escapeHtml(this._t("action.refresh"))}</span></button>
                        <button class="button-secondary picker-overflow-item" type="button" data-picker-new-folder="1" ${capabilities.can_create_folder ? "" : "disabled"}>${ICONS.plus}<span>${this._escapeHtml(this._t("action.new_folder"))}</span></button>
                        <button class="button-secondary picker-overflow-item" type="button" data-picker-upload-files="1" ${capabilities.can_upload ? "" : "disabled"}>${ICONS.upload}<span>${this._escapeHtml(this._t("action.upload_files"))}</span></button>
                        <button class="button-secondary picker-overflow-item" type="button" data-picker-upload-folder="1" ${capabilities.can_upload ? "" : "disabled"}>${ICONS.folder}<span>${this._escapeHtml(this._t("action.upload_folder"))}</span></button>
                      </div>
                    `
                    : ""
                  }
                </div>
              </div>
              <div class="picker-pathbar">
                <div class="picker-pathbar-main">
                  <p class="picker-pathbar-label">${this._escapeHtml(this._t("label.current_folder"))}</p>
                  <div class="picker-breadcrumbs">
                    ${breadcrumbs}
                  </div>
                </div>
              </div>
              <div class="picker-filebrowser-table-wrap ${isEmpty && !hasParentRow ? "empty" : ""} ${isEmpty && hasParentRow ? "has-empty-message" : ""}">
                ${loading || (!hasParentRow && empty) || `
                  <div class="picker-filebrowser-table">
                    ${hasParentRow ? `
                      <div class="picker-file-row folder parent" role="button" tabindex="0" data-picker-row-path="${this._escapeAttribute(`parent:${this._picker.parent_path}`)}" data-picker-row-index="0" data-picker-open="${this._escapeAttribute(this._picker.parent_path)}" data-picker-select-kind="file">
                        <div class="picker-file-row-main">
                          <span class="picker-file-name">
                            <span class="picker-file-kind" aria-hidden="true">${ICONS.folder}</span>
                            <span>..</span>
                          </span>
                          <span class="picker-file-meta"></span>
                          <span class="picker-file-size"></span>
                          <span class="picker-file-actions"></span>
                        </div>
                      </div>
                    ` :
                    ''}
                    ${items.map((item, index) => this._renderPickerItemRow(item, index + (this._picker.parent_path ? 1 : 0))).join("")}
                  </div>
                  ${hasParentRow && isEmpty ? `<p class="picker-empty picker-empty-overlay">${this._escapeHtml(this._t("empty.folder"))}</p>` : ""}
                `}
              </div>
              ${preview}
            </section>
          </div>
          ${this._renderPickerActionDialog()}
          <div class="picker-dialog-footer">
            <button class="button-secondary" type="button" data-picker-close="1">${this._escapeHtml(this._t("action.cancel"))}</button>
            <button
              class="button-primary"
              type="button"
              data-picker-choose="${this._escapeAttribute(selectedPath)}"
              ${canSelect ? "" : "disabled"}
            >${this._escapeHtml(this._t("action.select_folder"))}</button>
          </div>
        </div>
        </div>
        ${(this._pickerLoading || this._pickerNativeFileDialogOpen) ? `<div class="picker-loading-overlay" role="status" aria-label="${this._escapeAttribute(this._t("loading.items"))}"><span class="loading-spinner" aria-hidden="true"></span></div>` : ""}
      </div>
    `;
  }

  _renderRestartConfirmation() {
    if (!this._restartConfirmOpen) {
      return "";
    }

    const restartCopy = this._restartContext === "provider-refresh"
      ? (this._data?.restart_alert_note
        || this._t("notice.restart_providers"))
      : (this._data?.restart_note
        || this._t("notice.restart_saved"));

    return `
      <div class="confirm-overlay">
        <div class="confirm-dialog" role="dialog" aria-modal="true" aria-label="${this._escapeAttribute(this._t("aria.confirm_restart"))}">
          <h3 class="confirm-title">${this._escapeHtml(this._t("title.restart"))}</h3>
          <p class="confirm-copy">
            ${this._escapeHtml(restartCopy)}
          </p>
          <div class="confirm-actions">
            ${this._restarting
              ? ""
              : `<button class="button-secondary" type="button" data-restart-cancel="1">${this._escapeHtml(this._t("action.cancel"))}</button>`
            }
            <button class="button-restart" type="button" data-restart-confirm="1" ${this._restarting ? "disabled" : ""}>
              ${this._restarting
                ? `<span class="button-spinner" aria-hidden="true"></span>${this._escapeHtml(this._t("status.restarting"))}`
                : this._escapeHtml(this._t("action.restart_home_assistant"))
              }
            </button>
          </div>
        </div>
      </div>
    `;
  }

  _renderDiscardChangesConfirmation() {
    if (!this._discardChangesConfirmOpen) {
      return "";
    }

    const isNavigating = Boolean(this._pendingNavigationUrl || this._pendingRestartReason);

    return `
      <div class="confirm-overlay">
        <div class="confirm-dialog" role="dialog" aria-modal="true" aria-label="${this._escapeAttribute(this._t("aria.unsaved_changes"))}">
          <h3 class="confirm-title">${this._escapeHtml(this._t(isNavigating ? "title.save_changes" : "title.reset_changes"))}</h3>
          <p class="confirm-copy">${this._escapeHtml(this._t(isNavigating ? "notice.unsaved_changes" : "notice.discard_changes"))}</p>
          <div class="confirm-actions">
            <button class="button-secondary" type="button" data-discard-changes-cancel="1">${this._escapeHtml(this._t("action.cancel"))}</button>
            <button class="button-secondary" type="button" data-discard-changes-confirm="1">${this._escapeHtml(this._t("action.discard"))}</button>
            <button class="button-primary" type="button" data-discard-changes-save="1" ${this._saving || this._hasInvalidPathChanges() ? "disabled" : ""}>${this._escapeHtml(this._t("action.save"))}</button>
          </div>
        </div>
      </div>
    `;
  }

  _renderRandomChimeSetDeleteConfirmation() {
    const target = this._randomChimeSetDeleteTarget;
    if (!target) {
      return "";
    }

    const usageWarning = target.usedBy?.length
      ? `It is currently used by ${target.usedBy.join(", ")}.`
      : "";
    return `
      <div class="confirm-overlay">
        <div class="confirm-dialog" role="dialog" aria-modal="true" aria-label="Delete ${this._escapeAttribute(target.name || "Chime Set")} Chime Set">
          <h3 class="confirm-title">Delete &quot;${this._escapeHtml(target.name || "Chime Set")}&quot; Chime Set?</h3>
          ${usageWarning ? `<p class="confirm-copy">${this._escapeHtml(usageWarning)}</p>` : ""}
          <div class="confirm-actions">
            <button class="button-secondary" type="button" data-random-chime-set-delete-cancel="1">${this._escapeHtml(this._t("action.cancel"))}</button>
            <button class="button-danger" type="button" data-random-chime-set-delete-confirm="1">${this._escapeHtml(this._t("action.delete"))}</button>
          </div>
        </div>
      </div>
    `;
  }

  _renderChimeSetOffsetEditor() {
    const editor = this._chimeSetOffsetEditor;
    if (!editor) return "";
    const waveform = this._renderChimeSetWaveform(editor.waveform);
    const resetDisabled = Number(editor.offset) === Number(editor.initialOffset);
    const offsetValue = editor.editingOffset
      ? `<input class="chime-set-offset-title-input" data-chime-set-offset-input="1" type="number" step="1" inputmode="numeric" value="${this._escapeAttribute(editor.offset)}" aria-label="Chime offset in milliseconds" />`
      : `<button class="chime-set-offset-value" type="button" data-chime-set-offset-value="1" aria-label="Edit chime offset">${this._escapeHtml(editor.offset)} ms</button>`;
    return `<div class="confirm-overlay"><div class="confirm-dialog chime-set-offset-dialog" role="dialog" aria-modal="true" aria-label="Edit chime offset">
      <h3 class="confirm-title">${this._escapeHtml(editor.label)} Chime Offset: ${offsetValue}</h3>
      <p class="chime-set-offset-title-hint">Drag either audio block.</p>
      <div class="chime-set-offset-axis" data-chime-set-offset-axis="1" aria-hidden="true"></div>
      <div class="chime-set-offset-timeline ${editor.timelineReady ? "" : "initializing"}" data-chime-set-offset-timeline="1" aria-label="Chime and TTS audio timing">
        <div class="chime-set-offset-audio chime-set-offset-tts" data-chime-set-offset-audio="tts" role="slider" tabindex="0" aria-label="TTS audio position" aria-valuemin="-10000" aria-valuemax="10000" aria-valuenow="${this._escapeAttribute(editor.offset)}">
          <span class="chime-set-offset-audio-label">TTS audio</span>
        </div>
        <div class="chime-set-offset-audio chime-set-offset-waveform" data-chime-set-offset-audio="chime" role="slider" tabindex="0" aria-label="Chime waveform position" aria-valuemin="-10000" aria-valuemax="10000" aria-valuenow="${this._escapeAttribute(editor.offset)}">
          <svg data-chime-set-waveform="1" viewBox="0 0 200 40" preserveAspectRatio="none" aria-hidden="true">${waveform}</svg>
          <span class="chime-set-offset-audio-label">Chime</span>
        </div>
        <span class="chime-set-offset-overlap-line" data-chime-set-offset-overlap="start"></span>
        <span class="chime-set-offset-overlap-line" data-chime-set-offset-overlap="end"></span>
        <span class="chime-set-offset-playback-head ${editor.previewStarted ? "playing" : ""}" style="--chime-set-preview-duration: ${Number(editor.previewDuration) || 1}s"></span>
      </div>
      <div class="chime-set-offset-hint-row"><button class="button-secondary chime-set-offset-preview-button ${editor.previewPlaying ? "stop" : ""}" type="button" data-chime-set-offset-preview="1">${editor.previewPlaying ? ICONS.stop : ICONS.play}<span>${editor.previewPlaying ? "Stop" : "Preview"}</span></button></div>
      <div class="confirm-actions"><button class="button-secondary" type="button" data-chime-set-offset-reset="1" ${resetDisabled ? "disabled" : ""}>${this._escapeHtml(this._t("action.reset"))}</button><button class="button-primary" type="button" data-chime-set-offset-close="1">${resetDisabled ? this._escapeHtml(this._t("action.close")) : "Done"}</button></div>
    </div></div>`;
  }

  _renderPickerPreview() {
    if (this._picker?.field_key !== "custom_chimes_path") {
      return "";
    }

    const previewFiles = this._picker?.preview_files || [];
    return `
      <div class="picker-preview">
        ${previewFiles.length > 0 ? `
          <p class="picker-preview-title centered">
            ${this._escapeHtml(this._t("picker.audio_files_found", { count: previewFiles.length }))}
          </p>` :

          `<p class="picker-preview-title centered">
            ${this._escapeHtml(this._t("picker.no_audio_files"))}
          </p>`
        }
      </div>`;
  }

  _getVisiblePickerItems() {
    const filter = String(this._pickerFilter || "").trim().toLowerCase();
    const items = this._picker?.items || [];
    if (!filter) {
      return items;
    }
    return items.filter((item) => {
      const haystack = [
        item?.name || "",
        item?.path || "",
        item?.extension || "",
      ].join(" ").toLowerCase();
      return haystack.includes(filter);
    });
  }

  _renderPickerItemRow(item, rowIndex = 0) {
    const canOpen = Boolean(item?.is_dir);
    const isSelected = (item?.path || "") === (this._pickerSelectedPath || "");
    const canRename = Boolean(item?.path && this._picker?.capabilities?.can_rename);
    const canDelete = Boolean(item?.path && this._picker?.capabilities?.can_delete);
    const canPreviewAudio = Boolean(item?.is_audio && item?.audio_preview_url);
    const isPlaying = canPreviewAudio && (item?.path || "") === this._pickerPlayingPath;
    const isLoadingAudio = canPreviewAudio && (item?.path || "") === this._pickerAudioLoadingPath;
    return `
      <div
        class="picker-file-row ${item?.is_dir ? "folder" : "file"} ${isSelected ? "selected" : ""}"
        role="button"
        tabindex="0"
        data-picker-row-path="${this._escapeAttribute(item?.path || "")}"
        data-picker-row-index="${this._escapeAttribute(String(rowIndex))}"
        data-picker-select="${this._escapeAttribute(item?.path || "")}"
        data-picker-select-kind="${item?.is_dir ? "directory" : "file"}"
      >
        <div class="picker-file-row-main">
          <span class="picker-file-name">
            <span class="picker-file-kind ${item?.is_audio ? "audio" : ""}" aria-hidden="true">${item?.is_dir ? ICONS.folder : item?.is_audio ? ICONS.music : ICONS.file}</span>
            ${canOpen
              ? `<button class="picker-file-open" type="button" data-picker-open="${this._escapeAttribute(item.path)}">${this._escapeHtml(item?.name || "")}</button>`
              : `<span class="picker-file-name-text">${this._escapeHtml(item?.name || "")}</span>`
            }
          </span>
          <span class="picker-file-meta">${this._escapeHtml(this._formatPickerModifiedAt(item?.modified_at))}</span>
          <span class="picker-file-size">${this._escapeHtml(item?.size_label || "")}</span>
        </div>
        <span class="picker-file-actions">
          ${canPreviewAudio
            ? `<button
                class="button-secondary icon-only-button ${isPlaying ? "preview-playing" : ""}"
                ${this._previewPlayingStyle(isPlaying, this._pickerPreviewDuration)}
                type="button"
                data-picker-audio-toggle="${this._escapeAttribute(item?.path || "")}"
                data-picker-audio-url="${this._escapeAttribute(item?.audio_preview_url || "")}"
                aria-label="${this._escapeAttribute(this._t(isPlaying ? "aria.pause_named" : "aria.play_named", { title: item?.name || this._t("label.audio_file") }))}"
                title="${this._escapeAttribute(this._t(isPlaying ? "action.pause_preview" : isLoadingAudio ? "action.loading_preview" : "action.play_preview"))}"
              >${isLoadingAudio ? '<span class="button-spinner" aria-hidden="true"></span>' : isPlaying ? ICONS.pause : ICONS.play}</button>`
            : ""
          }
          <button
            class="button-secondary icon-only-button"
            type="button"
            data-picker-rename="${this._escapeAttribute(item?.path || "")}"
            data-picker-name="${this._escapeAttribute(item?.name || "")}"
            aria-label="${this._escapeAttribute(this._t("aria.rename_named", { title: item?.name || this._t("label.item") }))}"
            title="${this._escapeAttribute(this._t("action.rename"))}"
            ${canRename ? "" : "disabled"}
          >${ICONS.pencil}</button>
          <button
            class="button-danger icon-only-button"
            type="button"
            data-picker-delete="${this._escapeAttribute(item?.path || "")}"
            data-picker-name="${this._escapeAttribute(item?.name || "")}"
            aria-label="${this._escapeAttribute(this._t("aria.delete_named", { title: item?.name || this._t("label.item") }))}"
            title="${this._escapeAttribute(this._t("action.delete"))}"
            ${canDelete ? "" : "disabled"}
          >${ICONS.trash}</button>
        </span>
      </div>
    `;
  }

  _renderPickerActionDialog() {
    if (!this._pickerAction) {
      return "";
    }

    const isDelete = this._pickerAction.mode === "delete";
    const isUpload = this._pickerAction.mode === "upload";
    const isUploadConflicts = this._pickerAction.mode === "upload_conflicts";
    const isUploadFolder = isUpload && Boolean(this._pickerAction.directory);
    const actionLabel = isDelete
      ? this._t("action.delete")
      : isUploadConflicts
        ? this._t("action.overwrite_existing")
      : isUpload
        ? this._t("action.upload")
      : this._pickerAction.mode === "rename"
        ? this._t("action.rename")
        : this._t("action.create_folder");
    const secondaryLabel = isUploadConflicts && this._pickerAction.nonExistingCount > 0
      ? this._t("action.upload_non_existing", { count: this._pickerAction.nonExistingCount })
      : "";
    const error = this._pickerAction.error
      ? `<div class="message error">${this._escapeHtml(this._pickerAction.error)}</div>`
      : "";
    const inputMarkup = isDelete || isUpload || isUploadConflicts
      ? ""
      : `
        <div class="picker-action-field">
          <label for="picker-action-input">${this._escapeHtml(this._t(this._pickerAction.mode === "rename" ? "label.new_name" : "label.folder_name"))}</label>
          <input
            id="picker-action-input"
            class="control"
            data-picker-action-input="1"
            type="text"
            value="${this._escapeAttribute(this._pickerAction.value || "")}"
            placeholder="${this._escapeAttribute(this._pickerAction.placeholder || "")}"
            ${this._pickerBusy ? "disabled" : ""}
          />
        </div>
      `;

    return `
      <div class="picker-action-overlay" role="presentation">
        <div class="picker-action-dialog ${isUploadConflicts ? "conflicts" : ""} ${isUploadFolder ? "upload-folder" : ""}" role="dialog" aria-modal="true" aria-label="${this._escapeAttribute(this._pickerAction.title || actionLabel)}">
          <div class="picker-action-header">
            <div class="picker-action-header-bar">
              <h3 class="picker-action-title">${this._escapeHtml(this._pickerAction.title || actionLabel)}</h3>
              ${isUploadConflicts
                ? `<button class="button-secondary icon-only-button picker-action-close" type="button" data-picker-action-cancel="1" aria-label="${this._escapeAttribute(this._t("aria.close_overwrite"))}" title="${this._escapeAttribute(this._t("action.close"))}">${ICONS.close}</button>`
                : ""
              }
            </div>
            <p class="picker-action-copy">${this._escapeHtml(this._pickerAction.copy || "")}</p>
          </div>
          <div class="picker-action-form">
            ${error}
            ${inputMarkup}
            <div class="picker-action-actions">
              ${isUploadConflicts
                ? ""
                : `<button class="button-secondary" type="button" data-picker-action-cancel="1" ${this._pickerBusy ? "disabled" : ""}>${this._escapeHtml(this._t("action.cancel"))}</button>`
              }
              ${secondaryLabel
                ? `<button class="button-secondary" type="button" data-picker-action-secondary="1" ${this._pickerBusy ? "disabled" : ""}>${this._escapeHtml(secondaryLabel)}</button>`
                : ""
              }
              <button
                class="${isDelete ? "button-danger" : "button-primary"}"
                type="button"
                data-picker-action-submit="1"
                aria-busy="${this._pickerBusy ? "true" : "false"}"
                ${this._pickerBusy ? "disabled" : ""}
              >${this._pickerBusy ? '<span class="button-spinner" aria-hidden="true"></span>' : this._escapeHtml(actionLabel)}</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  _formatPickerModifiedAt(value) {
    if (!value) {
      return "";
    }
    try {
      return new Intl.DateTimeFormat(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }).format(new Date(value));
    } catch (_error) {
      return String(value);
    }
  }

  _buildInitialPathValidationState() {
    const state = {};
    for (const section of this._data?.sections || []) {
      for (const field of section.fields || []) {
        if (field.can_browse && field.path_validation) {
          state[field.key] = field.path_validation;
        }
      }
    }
    return state;
  }

  _getBrowsableFieldsNeedingValidation() {
    const fields = [];
    for (const section of this._data?.sections || []) {
      for (const field of section.fields || []) {
        if (field.can_browse && !this._pathValidationState?.[field.key]) {
          fields.push(field);
        }
      }
    }
    return fields;
  }

  _getPathValidationState(field) {
    if (!field?.can_browse) {
      return null;
    }
    return this._pathValidationState?.[field.key] || field.path_validation || null;
  }

  _schedulePathValidation(fieldKey, path) {
    if (!fieldKey) {
      return;
    }

    const existingTimer = this._pathValidationTimers?.[fieldKey];
    if (existingTimer) {
      window.clearTimeout(existingTimer);
    }

    this._pathValidationTimers = {
      ...(this._pathValidationTimers || {}),
      [fieldKey]: window.setTimeout(() => {
        delete this._pathValidationTimers[fieldKey];
        this._requestPathValidation(fieldKey, path);
      }, 250),
    };
  }

  async _requestPathValidation(fieldKey, path, { preserveInputState = true } = {}) {
    if (!fieldKey) {
      return;
    }

    try {
      const validation = await this._hass.callWS({
        type: "chime_tts/validate_path",
        field_key: fieldKey,
        path: String(path ?? ""),
      });
      this._pathValidationState = {
        ...(this._pathValidationState || {}),
        [fieldKey]: validation,
      };
      if (preserveInputState) {
        this._rerenderPreservingInputState();
      } else {
        this._renderPreservingScrollPosition();
      }
    } catch (error) {
      this._pathValidationState = {
        ...(this._pathValidationState || {}),
        [fieldKey]: {
          field_key: fieldKey,
          valid: false,
          tone: "error",
          message: error?.message || this._t("error.validate_folder"),
          badges: [],
        },
      };
      if (preserveInputState) {
        this._rerenderPreservingInputState();
      } else {
        this._renderPreservingScrollPosition();
      }
    }
  }

  _rerenderPreservingInputState(
    fieldKey = null,
    stabilizeScroll = false,
    forceRender = false,
  ) {
    const activeControl = this.shadowRoot.activeElement;
    const hasPreviewState = Boolean(
      this._previewRenderPending
      || this._fieldPreviewAudio
      || this._notifyPreviewAudio
      || this._fieldPreviewLoadingKey
      || this._fieldPreviewPlayingKey
      || this._notifyPreviewLoadingKey
      || this._notifyPreviewPlayingKey,
    );
    if (!forceRender && !hasPreviewState && this._isTextEntryOrDropdown(activeControl)) {
      this._renderTopbar(this._data || {});
      this._deferPanelRenderUntilBlur(activeControl);
      return;
    }

    const scrollElement = document.scrollingElement;
    const scrollTop = scrollElement?.scrollTop ?? window.scrollY ?? 0;
    const activeElement = this.shadowRoot.activeElement;
    const ancestorScrollPositions = this._captureAncestorScrollPositions(activeElement);
    // Re-focusing a native select after its change event can reopen its picker
    // on mobile browsers. The newly rendered select already has the selected
    // value, so only restore focus for controls that need cursor preservation.
    const shouldRestoreFocus = activeElement?.tagName !== "SELECT"
      && activeElement?.type !== "checkbox";
    const activeFieldKey = fieldKey || activeElement?.dataset?.field || null;
    const activeNotifyFieldKey = activeElement?.dataset?.notifyField || null;
    const activeNotifyIndex = activeElement?.dataset?.notifyIndex || null;
    const activeNotifyInlineTest = activeElement?.dataset?.notifyInlineTestMessage
      ? {
          index: activeElement?.dataset?.notifyIndex || null,
        }
      : null;
    const selectionStart = typeof activeElement?.selectionStart === "number"
      ? activeElement.selectionStart
      : null;
    const selectionEnd = typeof activeElement?.selectionEnd === "number"
      ? activeElement.selectionEnd
      : null;

    const restoreScrollPosition = () => {
      if (scrollElement) {
        scrollElement.scrollTop = scrollTop;
      } else {
        window.scrollTo(0, scrollTop);
      }
      ancestorScrollPositions.forEach(({ element, top, left }) => {
        element.scrollTop = top;
        element.scrollLeft = left;
      });
    };

    this._render({ force: forceRender || hasPreviewState });
    this._previewRenderPending = false;
    window.requestAnimationFrame(() => {
      restoreScrollPosition();
      // A complete panel render can change the page height after the first
      // frame (for example when a profile collapses), so restore once more.
      window.requestAnimationFrame(restoreScrollPosition);

      if (
        !shouldRestoreFocus
        || (!activeFieldKey && !activeNotifyFieldKey && !activeNotifyInlineTest)
      ) {
        return;
      }

      const nextField = activeFieldKey
        ? this.shadowRoot.querySelector(`[data-field="${CSS.escape(activeFieldKey)}"]`)
        : activeNotifyFieldKey
          ? this.shadowRoot.querySelector(
            `[data-notify-field="${CSS.escape(activeNotifyFieldKey)}"][data-notify-index="${CSS.escape(String(activeNotifyIndex))}"]`,
          )
          : this.shadowRoot.querySelector(
            `[data-notify-inline-test-message="1"][data-notify-index="${CSS.escape(String(activeNotifyInlineTest.index))}"]`,
          );
      if (!nextField) {
        return;
      }

      nextField.focus({ preventScroll: true });
      if (selectionStart !== null && selectionEnd !== null && typeof nextField.setSelectionRange === "function") {
        nextField.setSelectionRange(selectionStart, selectionEnd);
      }
    });
    if (stabilizeScroll) {
      // Expanding a split script field moves the clicked checkbox down. Home
      // Assistant's outer scroller applies that compensation after the next
      // paint, so restore once more after its layout update has settled.
      window.setTimeout(restoreScrollPosition, 100);
    }
  }

  _captureAncestorScrollPositions(element) {
    const positions = [];
    const seen = new Set();
    let current = element;
    while (current) {
      const parent = current.parentElement || current.getRootNode?.().host || null;
      if (!parent || seen.has(parent)) {
        break;
      }
      seen.add(parent);
      if (parent.scrollHeight > parent.clientHeight || parent.scrollWidth > parent.clientWidth) {
        positions.push({
          element: parent,
          top: parent.scrollTop,
          left: parent.scrollLeft,
        });
      }
      current = parent;
    }
    return positions;
  }

  _openRestartConfirmation(reason = "pending") {
    const restartReason = reason || "pending";
    const canRestartForReason = restartReason === "provider-refresh"
      || this._restartPending;
    if (!canRestartForReason || this._restarting) {
      return;
    }
    if (this._isDirty) {
      this._pendingRestartReason = restartReason;
      this._discardChangesConfirmOpen = true;
      this._render();
      return;
    }
    this._restartContext = restartReason;
    this._restartConfirmOpen = true;
    this._render();
  }

  _closeRestartConfirmation() {
    if (this._restarting) {
      return;
    }
    this._restartConfirmOpen = false;
    this._restartContext = null;
    this._render();
  }

  async _confirmRestart() {
    const restartContext = this._restartContext || "pending";
    const canRestartForReason = restartContext === "provider-refresh"
      || this._restartPending;
    if (!canRestartForReason || this._restarting) {
      return;
    }

    this._restarting = true;
    this._render();

    try {
      await this._hass.callService("homeassistant", "restart");
      this._restartPending = false;
      this._restartConfirmOpen = false;
      this._restartContext = null;
      this._data = {
        ...(this._data || {}),
        message: this._t("status.restart_requested"),
        message_type: "success",
      };
      this._showSaveResult("success");
    } catch (error) {
      this._data = {
        ...(this._data || {}),
        message: error?.message || this._t("error.restart"),
        message_type: "error",
      };
      this._showSaveResult("error");
    } finally {
      this._restarting = false;
      this._render();
    }
  }

  _handleBeforeUnload(event) {
    if (!this._isDirty || this._saving || this._allowUnload) {
      return;
    }
    event.preventDefault();
    // Browsers ignore custom wording. `true` is the most broadly supported
    // native-confirmation signal for reloads and other page-unload attempts.
    event.returnValue = true;
    return event.returnValue;
  }

  _handleNavigationClick(event) {
    if (
      !this._isDirty
      || this._saving
      || event.defaultPrevented
      || event.button !== 0
      || event.metaKey
      || event.ctrlKey
      || event.shiftKey
      || event.altKey
    ) {
      return;
    }

    const anchor = event.composedPath().find((node) => node instanceof HTMLAnchorElement);
    if (!anchor || anchor.target || anchor.hasAttribute("download")) {
      return;
    }

    let targetUrl;
    try {
      targetUrl = new URL(anchor.href, window.location.href);
    } catch (_error) {
      return;
    }
    if (targetUrl.href === window.location.href) {
      return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();
    this._pendingNavigationUrl = targetUrl.href;
    this._discardChangesConfirmOpen = true;
    this._render();
  }

  _requestResetAllChanges() {
    if (!this._isDirty) {
      this._resetAllChanges();
      return;
    }
    this._pendingNavigationUrl = "";
    this._discardChangesConfirmOpen = true;
    this._render();
  }

  _closeDiscardChangesConfirmation() {
    this._discardChangesConfirmOpen = false;
    this._pendingNavigationUrl = "";
    this._pendingRestartReason = null;
    this._render();
  }

  _confirmResetAllChanges() {
    const navigationUrl = this._pendingNavigationUrl;
    const restartReason = this._pendingRestartReason;
    this._discardChangesConfirmOpen = false;
    this._pendingNavigationUrl = "";
    this._pendingRestartReason = null;
    if (navigationUrl) {
      this._navigateAfterDiscard(navigationUrl);
      return;
    }
    this._resetAllChanges({ preserveRestart: Boolean(restartReason) });
    if (restartReason) {
      this._openRestartConfirmation(restartReason);
    }
  }

  async _saveUnsavedChanges() {
    await this._submit();
    if (!this._isDirty) {
      const navigationUrl = this._pendingNavigationUrl;
      const restartReason = this._pendingRestartReason;
      this._discardChangesConfirmOpen = false;
      this._pendingNavigationUrl = "";
      this._pendingRestartReason = null;
      if (navigationUrl) {
        this._navigateAfterDiscard(navigationUrl);
      } else if (restartReason) {
        this._openRestartConfirmation(restartReason);
      } else {
        this._render();
      }
    }
  }

  _navigateAfterDiscard(url) {
    this._allowUnload = true;
    window.location.assign(url);
  }

  _resetAllChanges({ preserveRestart = false } = {}) {
    const restartPending = this._restartPending;
    this._draftValues = { ...(this._data?.values || {}) };
    this._draftNotifyProfiles = this._cloneNotifyProfiles(this._data?.notify_profiles || []);
    this._clientErrors = {};
    this._notifyProfileClientErrors = [];
    this._notifyProfileTests = {};
    this._isDirty = false;
    this._pathValidationState = this._buildInitialPathValidationState();
    this._invalidPathOverrides = {};
    this._restartPending = preserveRestart ? restartPending : false;
    this._restartConfirmOpen = false;
    this._discardChangesConfirmOpen = false;
    this._pendingNavigationUrl = "";
    this._pendingRestartReason = null;
    this._restartContext = null;
    this._clearSaveResult();
    this._rerenderPreservingInputState();
  }

  _resetSection(sectionKey) {
    if (!sectionKey) {
      return;
    }

    const section = (this._data?.sections || []).find((item) => item.key === sectionKey);
    if (!section) {
      return;
    }

    if (section.kind === "notify_profiles") {
      this._draftNotifyProfiles = this._cloneNotifyProfiles(this._data?.notify_profiles || []);
      this._notifyProfileClientErrors = [];
      this._notifyProfileTests = {};
      this._isDirty = this._hasValueChanges();
      this._restartPending = false;
      this._restartConfirmOpen = false;
      this._restartContext = null;
      this._rerenderPreservingInputState();
      return;
    }

    if (section.kind === "chime_sets") {
      this._draftValues = {
        ...(this._draftValues || {}),
        chime_sets: this._cloneRandomChimeSets(this._data?.values?.chime_sets || []),
      };
      this._isDirty = this._hasValueChanges();
      this._rerenderPreservingInputState();
      return;
    }

    const nextDraftValues = { ...(this._draftValues || {}) };
    for (const field of section.fields || []) {
      nextDraftValues[field.key] = this._data?.values?.[field.key];
      if (this._clientErrors[field.key]) {
        delete this._clientErrors[field.key];
      }
      if (field.can_browse && field.path_validation) {
        this._pathValidationState = {
          ...(this._pathValidationState || {}),
          [field.key]: field.path_validation,
        };
      }
      if (field.can_browse && this._invalidPathOverrides?.[field.key]) {
        const nextOverrides = { ...(this._invalidPathOverrides || {}) };
        delete nextOverrides[field.key];
        this._invalidPathOverrides = nextOverrides;
      }
    }
    this._draftValues = nextDraftValues;
    this._isDirty = this._hasValueChanges();
    if (section.fields?.some((field) => field.key === "custom_chimes_path")) {
      this._restartPending = false;
      this._restartConfirmOpen = false;
      this._restartContext = null;
    }
    this._rerenderPreservingInputState();
  }

  _toggleAdvanced(sectionKey) {
    if (!sectionKey) {
      return;
    }
    this._animateHeightTransition(
      `[data-section-key="${this._escapeSelectorValue(sectionKey)}"]`,
      () => {
        const section = (this._data?.sections || []).find((item) => item.key === sectionKey);
        const expanded = !this._isAdvancedOpen(section || { key: sectionKey, fields: [] });
        this._advancedSections = {
          ...(this._advancedSections || {}),
          [sectionKey]: expanded,
        };
        this._applyAdvancedSectionState(sectionKey, expanded);
      },
    );
  }

  _isAdvancedOpen(section) {
    const explicit = this._advancedSections?.[section.key];
    if (explicit !== undefined) {
      return explicit;
    }
    return false;
  }

  _isConfigSectionExpanded(sectionKey) {
    return this._expandedConfigSections?.[sectionKey] === true;
  }

  _renderPreservingScrollPosition() {
    const activeControl = this.shadowRoot.activeElement;
    if (this._isTextEntryOrDropdown(activeControl)) {
      this._renderTopbar(this._data || {});
      this._deferPanelRenderUntilBlur(activeControl);
      return;
    }

    const scrollElement = document.scrollingElement;
    const scrollTop = scrollElement?.scrollTop ?? window.scrollY ?? 0;

    this._render();

    const restoreScrollPosition = () => {
      if (scrollElement) {
        scrollElement.scrollTop = scrollTop;
      } else {
        window.scrollTo(0, scrollTop);
      }
    };

    // Mobile browsers can apply scroll anchoring after the panel's new layout
    // has been measured. Restore again on the following frame so collapsing a
    // section does not move the viewport when the Chimes list is open.
    window.requestAnimationFrame(() => {
      restoreScrollPosition();
      window.requestAnimationFrame(restoreScrollPosition);
    });
  }

  _isTextEntryOrDropdown(element) {
    return this._hasActiveTextEntryFocus() || element?.tagName === "SELECT";
  }

  _rerenderAfterLogUpdate() {
    const activeControl = this.shadowRoot.activeElement;
    if (this._hasActiveInteractiveElement(activeControl)) {
      this._renderTopbar(this._data || {});
      this._deferPanelRenderUntilBlur(activeControl);
      return;
    }
    this._rerenderPreservingInputState();
  }

  _deferPanelRenderUntilBlur(element) {
    if (!(element instanceof HTMLElement) || element.dataset.deferPanelRender === "1") {
      return;
    }
    element.dataset.deferPanelRender = "1";
    element.addEventListener("blur", () => {
      delete element.dataset.deferPanelRender;
      // A synchronous render here removes a button that was clicked to move
      // focus away from this field, which prevents that button's click event
      // from firing. Let the click complete before redrawing the panel.
      window.setTimeout(() => this._renderPreservingScrollPosition(), 0);
    }, { once: true });
  }

  _toggleConfigSection(sectionKey) {
    if (!sectionKey) {
      return;
    }
    const updateSectionState = () => {
      const expanded = !this._isConfigSectionExpanded(sectionKey);
      this._expandedConfigSections = {
        ...(this._expandedConfigSections || {}),
        [sectionKey]: expanded,
      };
      this._renderPreservingScrollPosition();
    };

    // The Chime List can be much taller than the viewport on mobile. Rendering
    // it immediately avoids a second height transition that can reset a touch
    // scroll once momentum ends.
    if (sectionKey === "chime_list") {
      updateSectionState();
      return;
    }

    this._animateHeightTransition(
      `[data-config-section-card="${this._escapeSelectorValue(sectionKey)}"]`,
      updateSectionState,
    );
  }

  _shouldIgnoreConfigSectionCardToggle(event) {
    const target = event.target;
    if (!(target instanceof Element)) {
      return false;
    }

    if (event.type === "click" && window.getSelection && !window.getSelection().isCollapsed) {
      return true;
    }

    return Boolean(
      target.closest(
        [
          "a",
          "button",
          "input",
          "select",
          "textarea",
          "label",
          ".row-collapse",
          ".field-grid",
          ".advanced-toggle-row",
        ].join(", "),
      ),
    );
  }

  _isChapterExpanded(chapterKey) {
    return this._expandedChapters?.[chapterKey] === true;
  }

  _handleChapterToggleEvent(event) {
    if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") return;
    const toggle = event.composedPath().find(
      (node) => node instanceof Element && node.matches?.("[data-toggle-chapter]"),
    );
    if (!toggle) return;
    event.preventDefault();
    event.stopPropagation();
    this._toggleChapter(toggle.dataset.toggleChapter);
  }

  _toggleChapter(chapterKey) {
    if (!chapterKey) {
      return;
    }
    this._animateHeightTransition(
      `[data-chapter-key="${this._escapeSelectorValue(chapterKey)}"] .chapter-hero`,
      () => {
        const wasExpanded = this._isChapterExpanded(chapterKey);
        const expanded = !wasExpanded;
        this._expandedChapters = {
          ...(this._expandedChapters || {}),
          [chapterKey]: expanded,
        };
        this._renderPreservingScrollPosition();
        if (chapterKey === "logs" && !wasExpanded) {
          this._refreshLogs({ force: true });
        }
        this._syncLogsRefresh();
      },
    );
  }

  _isLogEventExpanded(eventId) {
    return this._expandedLogEvents?.[eventId] === true;
  }

  _toggleLogEvent(eventId) {
    if (!eventId) {
      return;
    }
    this._animateHeightTransition(
      `[data-log-event-id="${this._escapeSelectorValue(eventId)}"]`,
      () => {
        const expanded = !this._isLogEventExpanded(eventId);
        this._expandedLogEvents = {
          ...(this._expandedLogEvents || {}),
          [eventId]: expanded,
        };
        this._render();
      },
    );
  }

  _toggleAllLogEvents(mode) {
    const events = this._data?.log_events || [];
    const nextState = {};
    for (const event of events) {
      nextState[event.id] = mode === "expand";
    }
    this._expandedLogEvents = nextState;
    this._render();
  }

  async _loadDebugLogsState() {
    if (!this._hass?.callWS) return;
    try {
      const status = await this._hass.callWS({ type: "chime_tts/get_debug_log_status" });
      this._debugLogsEnabled = Boolean(status?.debug_enabled);
      this._debugLogsError = "";
    } catch (_error) {
      this._debugLogsError = this._t("error.debug_logs");
    }
  }

  async _setDebugLogsEnabled(enabled) {
    if (!this._hass?.callWS || this._debugLogsUpdating) return;
    const previousValue = this._debugLogsEnabled;
    this._debugLogsEnabled = Boolean(enabled);
    this._debugLogsUpdating = true;
    this._debugLogsError = "";
    this._renderPreservingScrollPosition();
    try {
      await this._hass.callWS({
        type: "logger/integration_log_level",
        integration: "chime_tts",
        level: enabled ? "DEBUG" : "NOTSET",
        persistence: enabled ? "permanent" : "none",
      });
      await this._loadDebugLogsState();
    } catch (_error) {
      this._debugLogsEnabled = previousValue;
      this._debugLogsError = this._t("error.debug_logs");
    } finally {
      this._debugLogsUpdating = false;
      this._renderPreservingScrollPosition();
    }
  }

  _clearLogsRefreshTimer() {
    if (this._logsRefreshTimer) {
      window.clearTimeout(this._logsRefreshTimer);
      this._logsRefreshTimer = null;
    }
  }

  _shouldRefreshLogs() {
    return Boolean(
      this._hass
      && !this._loading
      && !this._saving
      && this._isChapterExpanded("logs")
      && !this._picker
      && !this._hasActiveInteractiveElement()
      && !this._hasActiveLogTextSelection()
      && document.visibilityState === "visible"
    );
  }

  _hasActiveInteractiveElement(element = this.shadowRoot?.activeElement) {
    return element instanceof HTMLElement
      && element.matches(
        'input, textarea, select, button, a[href], [contenteditable="true"], [tabindex]:not([tabindex="-1"])',
      );
  }

  _hasActiveDropdownFocus() {
    const activeElement = this.shadowRoot?.activeElement;
    if (!activeElement) {
      return false;
    }
    return activeElement.tagName === "SELECT";
  }

  _hasActiveTextEntryFocus() {
    const activeElement = this.shadowRoot?.activeElement;
    if (!(activeElement instanceof HTMLElement)) {
      return false;
    }

    if (activeElement.tagName === "TEXTAREA") {
      return true;
    }

    if (activeElement.tagName !== "INPUT") {
      return activeElement.isContentEditable;
    }

    const inputType = String(activeElement.getAttribute("type") || "text").toLowerCase();
    return !["checkbox", "radio", "range", "button", "submit", "reset"].includes(inputType);
  }

  _hasActiveLogTextSelection() {
    const selection = window.getSelection ? window.getSelection() : null;
    if (!selection || selection.isCollapsed || selection.rangeCount === 0) {
      return false;
    }

    const anchorNode = selection.anchorNode;
    const focusNode = selection.focusNode;
    const root = this.shadowRoot;
    if (!root || !anchorNode || !focusNode) {
      return false;
    }

    const anchorElement = anchorNode.nodeType === Node.ELEMENT_NODE ? anchorNode : anchorNode.parentElement;
    const focusElement = focusNode.nodeType === Node.ELEMENT_NODE ? focusNode : focusNode.parentElement;
    return Boolean(
      anchorElement?.closest(".log-event-body")
      || focusElement?.closest(".log-event-body")
    );
  }

  _syncLogsRefresh() {
    this._clearLogsRefreshTimer();
    if (!this._shouldRefreshLogs()) {
      return;
    }
    this._logsRefreshTimer = window.setTimeout(() => {
      this._logsRefreshTimer = null;
      this._refreshLogs();
      this._refreshDebugLogsState();
    }, 2000);
  }

  async _refreshDebugLogsState() {
    if (!this._shouldRefreshLogs() || this._debugLogsUpdating) return;
    const previousValue = this._debugLogsEnabled;
    await this._loadDebugLogsState();
    if (this._debugLogsEnabled !== previousValue) this._renderPreservingScrollPosition();
  }

  _getLogEventsSignature(events) {
    return JSON.stringify((events || []).map((event) => ({
      id: event?.id || "",
      title: event?.title || "",
      summary: event?.summary || "",
      meta: this._formatLogEventMeta(event || {}),
      raw_logs: (event?.raw_logs || []).map((entry) => ({
        timestamp: entry?.timestamp || "",
        level: entry?.level || "",
        logger: entry?.logger || "",
        message: entry?.message || "",
      })),
      copy_yaml: event?.copy_yaml || "",
      can_repeat: Boolean(event?.can_repeat),
      has_error: Boolean(event?.has_error),
      row_color: event?.row_color || "",
      type: event?.type || "",
    })));
  }

  async _refreshLogs({ showOpeningSpinner = false, force = false } = {}) {
    if (this._logsRefreshInFlight || (!force && !this._shouldRefreshLogs())) {
      if (showOpeningSpinner) {
        this._logsOpeningRefresh = false;
      }
      this._syncLogsRefresh();
      return;
    }
    this._logsRefreshInFlight = true;
    try {
      const previousLogEvents = this._data?.log_events || [];
      const previousSignature = this._getLogEventsSignature(previousLogEvents);
      const result = await this._hass.callWS({ type: "chime_tts/get_logs" });
      const nextLogEvents = result?.log_events || [];
      const nextSignature = this._getLogEventsSignature(nextLogEvents);
      const logsChanged = nextSignature !== previousSignature;
      const wasShowingSpinner = this._logsOpeningRefresh;
      if (logsChanged) {
        this._data = {
          ...(this._data || {}),
          log_events: nextLogEvents,
        };
      }
      this._logsOpeningRefresh = false;
      this._logsHydrated = true;
      this._logsLoaded = true;
      if (wasShowingSpinner || (logsChanged && this._isChapterExpanded("logs"))) {
        this._rerenderAfterLogUpdate();
      }
    } catch (_error) {
      const wasShowingSpinner = this._logsOpeningRefresh;
      this._logsOpeningRefresh = false;
      if (wasShowingSpinner && this._isChapterExpanded("logs")) {
        this._rerenderAfterLogUpdate();
      }
      this._syncLogsRefresh();
    } finally {
      this._logsRefreshInFlight = false;
      this._syncLogsRefresh();
    }
  }

  _formatLogEventMeta(event) {
    const parts = [];
    if (event.type === "integration_initiation") {
      parts.push(this._t("log.integration_initiation"));
    } else if (event.type === "notification_call") {
      parts.push(this._t("log.notification"));
    } else if (event.type === "configuration_update") {
      parts.push(this._t("log.configuration_update"));
    } else if (event.type === "action_call") {
      parts.push(this._t("log.action_call"));
    } else if (event.type === "warning") {
      parts.push(this._t("log.warning"));
    } else if (event.type === "error") {
      parts.push(this._t("log.error"));
    }
    if (event.started_at) {
      parts.push(this._formatTimestamp(event.started_at));
    }
    if (event.error_count) {
      parts.push(`${event.error_count} error${event.error_count === 1 ? "" : "s"}`);
    }
    return parts.join(" • ");
  }

  _getLogEventIcon(event) {
    if (this._getLogEventIconClass(event) !== "normal") {
      return ICONS.alert;
    }
    if (event.type === "integration_initiation") {
      return ICONS.check;
    }
    if (event.type === "custom_chimes_update") {
      return ICONS.folder;
    }
    if (event.title === "Action call: chime_tts.replay") {
      return ICONS.repeat;
    }
    if (event.title === "Action call: chime_tts.clear_cache") {
      return ICONS.trash;
    }
    if (
      event.title === "Action call: chime_tts.say"
      || event.title === "Action call: chime_tts.say_url"
    ) {
      return ICONS.check;
    }
    return ICONS.check;
  }

  _getLogEventIconClass(event) {
    if (!event) {
      return "normal";
    }

    if (event.type === "error" || event.row_color === "error") {
      return "error";
    }
    if (event.type === "warning" || event.row_color === "warning") {
      return "warning";
    }

    const isSayAction = event.title === "Action call: chime_tts.say"
      || event.title === "Action call: chime_tts.say_url";
    if (!isSayAction) {
      return event.has_error ? "error" : "normal";
    }

    if (event.has_error || this._eventHasLogLevel(event, ["error", "critical", "fatal"])) {
      return "error";
    }

    if (this._eventHasLogLevel(event, ["warning", "warn"])) {
      return "warning";
    }

    return "normal";
  }

  _eventHasLogLevel(event, levels) {
    const allowedLevels = new Set((levels || []).map((level) => String(level || "").toLowerCase()));
    return (event?.raw_logs || []).some((entry) => allowedLevels.has(String(entry?.level || "").toLowerCase()));
  }

  _formatTimestamp(value) {
    try {
      return new Intl.DateTimeFormat(undefined, {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }).format(new Date(value));
    } catch (_error) {
      return String(value || "");
    }
  }

  _getLogCopyState(eventId) {
    return {
      logs: false,
      yaml: false,
      ...((this._logCopyState || {})[eventId] || {}),
    };
  }

  _scheduleLogCopyReset(eventId, key) {
    this._clearLogCopyTimer(eventId, key);
    const timerKey = `${eventId}:${key}`;
    this._logCopyTimers = {
      ...(this._logCopyTimers || {}),
      [timerKey]: window.setTimeout(() => {
        this._clearLogCopyTimer(eventId, key);
        const current = this._getLogCopyState(eventId);
        this._logCopyState = {
          ...(this._logCopyState || {}),
          [eventId]: {
            ...current,
            [key]: false,
          },
        };
        this._render();
      }, 2000),
    };
  }

  _clearLogCopyTimer(eventId, key) {
    const timerKey = `${eventId}:${key}`;
    const timer = this._logCopyTimers?.[timerKey];
    if (!timer) {
      return;
    }
    window.clearTimeout(timer);
    const nextTimers = { ...(this._logCopyTimers || {}) };
    delete nextTimers[timerKey];
    this._logCopyTimers = nextTimers;
  }

  _clearAllLogCopyTimers() {
    for (const timerKey of Object.keys(this._logCopyTimers || {})) {
      const timer = this._logCopyTimers[timerKey];
      if (timer) {
        window.clearTimeout(timer);
      }
    }
    this._logCopyTimers = {};
  }

  _getRawLogsText(event) {
    return (event?.raw_logs || [])
      .map((entry) => `[${entry.timestamp}] ${String(entry.level || "").toUpperCase()} ${entry.logger}: ${entry.message}`)
      .join("\n");
  }

  async _copyLogRaw(eventId) {
    const event = (this._data?.log_events || []).find((item) => item.id === eventId);
    const rawLogs = this._getRawLogsText(event);
    if (!rawLogs) {
      return;
    }
    try {
      await navigator.clipboard.writeText(rawLogs);
      this._logCopyState = {
        ...(this._logCopyState || {}),
        [eventId]: {
          ...this._getLogCopyState(eventId),
          logs: true,
        },
      };
      this._scheduleLogCopyReset(eventId, "logs");
      this._render();
    } catch (_error) {
      this._data = {
        ...(this._data || {}),
        message: this._t("error.copy_logs"),
        message_type: "error",
      };
      this._render();
    }
  }

  async _copyLogYaml(eventId) {
    const event = (this._data?.log_events || []).find((item) => item.id === eventId);
    if (!event?.copy_yaml) {
      return;
    }
    try {
      await navigator.clipboard.writeText(event.copy_yaml);
      this._logCopyState = {
        ...(this._logCopyState || {}),
        [eventId]: {
          ...this._getLogCopyState(eventId),
          yaml: true,
        },
      };
      this._scheduleLogCopyReset(eventId, "yaml");
      this._render();
    } catch (_error) {
      this._data = {
        ...(this._data || {}),
        message: this._t("error.copy_yaml"),
        message_type: "error",
      };
    }
    this._render();
  }

  async _repeatLogAction(eventId) {
    if (!eventId) {
      return;
    }
    try {
      this._data = await this._hass.callWS({
        type: "chime_tts/repeat_log_action",
        event_id: eventId,
      });
      this._draftValues = { ...(this._data?.values || {}) };
      this._draftNotifyProfiles = this._cloneNotifyProfiles(this._data?.notify_profiles || []);
      this._isDirty = false;
      this._clientErrors = {};
      this._notifyProfileClientErrors = [];
    } catch (error) {
      this._data = {
        ...(this._data || {}),
        message: error?.message || this._t("error.repeat"),
        message_type: "error",
      };
    }
    this._render();
  }

  _isSectionDirty(section) {
    if (section.kind === "notify_profiles") {
      return this._hasNotifyProfileChanges();
    }
    return (section.fields || []).some((field) => this._isFieldChanged(field.key));
  }

  _isFieldChanged(fieldKey) {
    const savedValues = this._data?.values || {};
    const draftValues = this._draftValues || {};
    return this._normalizeForCompare(savedValues[fieldKey], fieldKey) !== this._normalizeForCompare(draftValues[fieldKey], fieldKey);
  }

  _isNotifyProfileFieldChanged(index, fieldKey) {
    const savedProfile = (this._data?.notify_profiles || [])[index] || {};
    const draftProfile = (this._draftNotifyProfiles || [])[index] || {};
    return this._normalizeForCompare(savedProfile[fieldKey]) !== this._normalizeForCompare(draftProfile[fieldKey]);
  }

  _isNotifyProfileDirty(index) {
    const defaults = this._buildEmptyNotifyProfile();
    const savedProfile = {
      ...defaults,
      ...((this._data?.notify_profiles || [])[index] || {}),
    };
    const draftProfile = {
      ...defaults,
      ...((this._draftNotifyProfiles || [])[index] || {}),
    };
    const keys = new Set([...Object.keys(savedProfile), ...Object.keys(draftProfile)]);
    return [...keys].some((key) => this._normalizeForCompare(savedProfile[key]) !== this._normalizeForCompare(draftProfile[key]));
  }

  _getRestartRequiredChangedFields() {
    const restartKeys = this._data?.restart_required_field_keys || [];
    const labels = new Map();
    for (const section of this._data?.sections || []) {
      for (const field of section.fields || []) {
        labels.set(field.key, field.label);
      }
    }
    return restartKeys
      .filter((fieldKey) => this._isFieldChanged(fieldKey))
      .map((fieldKey) => ({ key: fieldKey, label: labels.get(fieldKey) || fieldKey }));
  }

  _useInvalidPathAnyway(fieldKey) {
    if (!fieldKey) {
      return;
    }
    this._invalidPathOverrides = {
      ...(this._invalidPathOverrides || {}),
      [fieldKey]: true,
    };
    this._render();
  }

  _setPathSuggestion(fieldKey, path) {
    if (!fieldKey || !path) {
      return;
    }
    const nextOverrides = { ...(this._invalidPathOverrides || {}) };
    delete nextOverrides[fieldKey];
    this._invalidPathOverrides = nextOverrides;
    this._draftValues = {
      ...(this._draftValues || {}),
      [fieldKey]: path,
    };
    this._isDirty = this._hasValueChanges();
    this._schedulePathValidation(fieldKey, path);
    this._rerenderPreservingInputState(fieldKey);
  }

  _captureSaveFocusState() {
    const element = this.shadowRoot?.activeElement;
    if (!(element instanceof HTMLElement) || element.id === "save-top") {
      return null;
    }

    const selector = element.dataset.field
      ? `[data-field="${CSS.escape(element.dataset.field)}"]`
      : element.dataset.notifyField
        ? `[data-notify-field="${CSS.escape(element.dataset.notifyField)}"][data-notify-index="${CSS.escape(String(element.dataset.notifyIndex || ""))}"]`
        : element.dataset.randomSetName !== undefined
          ? `[data-random-set-name="${CSS.escape(element.dataset.randomSetName)}"]`
          : null;
    if (!selector) {
      return null;
    }

    return {
      element,
      selector,
      selectionStart: typeof element.selectionStart === "number" ? element.selectionStart : null,
      selectionEnd: typeof element.selectionEnd === "number" ? element.selectionEnd : null,
    };
  }

  _restoreSaveFocusState(focusState) {
    if (!focusState) {
      return;
    }
    const element = this.shadowRoot?.querySelector(focusState.selector);
    if (!(element instanceof HTMLElement)) {
      return;
    }
    element.focus({ preventScroll: true });
    if (
      focusState.selectionStart !== null
      && focusState.selectionEnd !== null
      && typeof element.setSelectionRange === "function"
    ) {
      element.setSelectionRange(focusState.selectionStart, focusState.selectionEnd);
    }
  }

  async _submitFromSaveButton() {
    const focusState = this._captureSaveFocusState();
    focusState?.element.blur();
    try {
      await this._submit();
    } finally {
      this._restoreSaveFocusState(focusState);
    }
  }

  async _submit() {
    if (this._saving || !this._isDirty || this._hasInvalidPathChanges()) {
      return;
    }

    this._clientErrors = this._validateRequiredFields();
    if (
      Object.keys(this._clientErrors).length > 0
      || this._notifyProfileClientErrors.some((profileErrors) => Object.keys(profileErrors || {}).length > 0)
    ) {
      this._render();
      this._scrollToFirstValidationError();
      return;
    }

    const values = { ...this._draftValues };
    const notifyProfiles = this._cloneNotifyProfiles(this._draftNotifyProfiles || []);
    this._saving = true;
    this._clearSaveResult();
    this._render();

    try {
      const saveResult = await this._hass.callWS({
        type: "chime_tts/save_settings",
        values,
        notify_profiles: notifyProfiles,
        allow_invalid_paths: Object.keys(this._invalidPathOverrides || {}).filter((fieldKey) => this._invalidPathOverrides[fieldKey]),
      });
      this._data = { ...(this._data || {}), ...saveResult };
      const hasValidationErrors = Object.keys(this._data?.errors || {}).length > 0;
      this._draftValues = hasValidationErrors
        ? values
        : { ...(this._data?.values || {}) };
      this._draftNotifyProfiles = hasValidationErrors
        ? this._cloneNotifyProfiles(notifyProfiles)
        : this._cloneNotifyProfiles(this._data?.notify_profiles || []);
      this._isDirty = hasValidationErrors;
      this._clientErrors = {};
      this._notifyProfileClientErrors = [];
      this._notifyProfileTests = {};
      this._pathValidationState = this._buildInitialPathValidationState();
      this._invalidPathOverrides = {};
      this._restartPending = Boolean(this._data?.restart_required);
      this._restartConfirmOpen = this._restartPending;
      if (this._restartPending) {
        this._clearSaveResult();
      } else if (this._data?.message_type === "success" && this._data?.message) {
        this._showSaveResult("success");
        this._scheduleMessageClear();
      }
      if (!hasValidationErrors && this._data?.message_type === "success") {
        void this._refreshSavedSettingsMetadata();
      }
    } catch (error) {
      this._data = {
        ...(this._data || {}),
        message: error?.message || this._t("error.save"),
        message_type: "error",
      };
      this._showSaveResult("error");
    } finally {
      this._saving = false;
      this._render();
    }
  }

  _handleFieldChange(event) {
    const field = event.currentTarget;
    const key = field?.dataset?.field;
    if (!key) {
      return;
    }

    const nextValue = field.type === "checkbox" ? field.checked : field.value;
    if (key === "custom_chimes_path") {
      this._restartPending = false;
      this._restartConfirmOpen = false;
    }
    if (this._invalidPathOverrides?.[key]) {
      const nextOverrides = { ...(this._invalidPathOverrides || {}) };
      delete nextOverrides[key];
      this._invalidPathOverrides = nextOverrides;
    }
    if (key === "chime_path" || key === "end_chime_path") {
      this._stopFieldPreviewAudio();
    }
    const nextDraftValues = {
      ...(this._draftValues || {}),
      [key]: nextValue,
    };
    if (key === "default_pre_script_shared_key" && nextValue) {
      nextDraftValues.default_pre_script_say_url_key = "";
    }
    if (key === "default_post_script_shared_key" && nextValue) {
      nextDraftValues.default_post_script_say_url_key = "";
    }
    this._draftValues = nextDraftValues;
    if (this._clientErrors[key]) {
      const nextErrors = { ...(this._clientErrors || {}) };
      delete nextErrors[key];
      this._clientErrors = nextErrors;
    }
    this._isDirty = this._hasValueChanges();
    if (this._isPathFieldKey(key)) {
      this._schedulePathValidation(key, nextValue);
    }
    this._rerenderPreservingInputState(
      key,
      key === "default_pre_script_shared_key"
        || key === "default_post_script_shared_key",
      field.tagName === "SELECT",
    );
  }

  _randomChimeSetsDraft() {
    return Array.isArray(this._draftValues?.chime_sets)
      ? this._draftValues.chime_sets.map((chimeSet) => ({
        ...chimeSet,
        chimes: Array.isArray(chimeSet.chimes) ? [...chimeSet.chimes] : [],
        offsets: { ...(chimeSet.offsets || {}) },
      }))
      : [];
  }

  _cloneRandomChimeSets(sets) {
    return Array.isArray(sets) ? sets.map((chimeSet) => ({
      ...chimeSet,
      chimes: Array.isArray(chimeSet.chimes) ? [...chimeSet.chimes] : [],
      offsets: { ...(chimeSet.offsets || {}) },
    })) : [];
  }

  _randomChimeSetStructureChanged() {
    const savedIds = new Set((this._data?.values?.chime_sets || []).map((chimeSet) => chimeSet?.id).filter(Boolean));
    const draftIds = new Set(this._randomChimeSetsDraft().map((chimeSet) => chimeSet?.id).filter(Boolean));
    return savedIds.size !== draftIds.size || [...savedIds].some((id) => !draftIds.has(id));
  }

  _hasUnsavedRandomChimeSet() {
    const savedIds = new Set((this._data?.values?.chime_sets || []).map((chimeSet) => chimeSet?.id).filter(Boolean));
    return this._randomChimeSetsDraft().some((chimeSet) => chimeSet?.id && !savedIds.has(chimeSet.id));
  }

  _setRandomChimeSetsDraft(sets) {
    this._draftValues = { ...(this._draftValues || {}), chime_sets: sets };
    if (this._clientErrors.chime_sets) {
      const errors = { ...(this._clientErrors || {}) };
      delete errors.chime_sets;
      this._clientErrors = errors;
    }
    this._isDirty = this._hasValueChanges();
    this._rerenderPreservingInputState();
  }

  _addRandomChimeSet() {
    const sets = this._randomChimeSetsDraft();
    const id = globalThis.crypto?.randomUUID?.() || `set-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    sets.unshift({ id, name: "", chimes: [] });
    this._expandedRandomChimeSets = {
      ...this._offsetNotifyProfileState(this._expandedRandomChimeSets, 1),
      0: true,
    };
    this._setRandomChimeSetsDraft(sets);
  }

  _updateRandomChimeSetName(index, name) {
    const sets = this._randomChimeSetsDraft();
    if (!sets[index]) return;
    sets[index].name = name;
    this._setRandomChimeSetsDraft(sets);
  }

  _toggleRandomChimeSetMember(index, value, checked) {
    const sets = this._randomChimeSetsDraft();
    if (!sets[index]) return;
    const members = new Set(sets[index].chimes || []);
    if (checked) members.add(value);
    else members.delete(value);
    sets[index].chimes = [...members];
    this._setRandomChimeSetsDraft(sets);
  }

  _openChimeSetOffsetEditor(index, member, label = member) {
    const chimeSet = this._randomChimeSetsDraft()[index];
    if (!chimeSet || !chimeSet.chimes?.includes(member)) return;
    this._chimeSetOffsetEditor = {
      index,
      member,
      label,
      offset: String(chimeSet.offsets?.[member] ?? 0),
      initialOffset: String(chimeSet.offsets?.[member] ?? 0),
      waveform: this._chimeSetWaveformCache.get(member),
      chimeDuration: this._chimeSetDurationCache.get(member) || 1000,
      timelineReady: this._chimeSetDurationCache.has(member),
    };
    this._render();
    this._loadChimeSetWaveform(member);
  }

  _openChimeOffsetEditor(member, label = member) {
    if (!member) return;
    const offsets = this._draftValues?.chime_offsets || {};
    this._chimeSetOffsetEditor = {
      kind: "chime",
      member,
      label,
      offset: String(offsets[member] ?? 0),
      initialOffset: String(offsets[member] ?? 0),
      waveform: this._chimeSetWaveformCache.get(member),
      chimeDuration: this._chimeSetDurationCache.get(member) || 1000,
      timelineReady: this._chimeSetDurationCache.has(member),
    };
    this._render();
    this._loadChimeSetWaveform(member);
  }

  _renderChimeSetWaveform(samples) {
    if (!Array.isArray(samples)) {
      return '<text x="100" y="24" fill="currentColor" text-anchor="middle" font-size="11">Loading waveform…</text>';
    }
    if (samples.length === 0) {
      return '<text x="100" y="24" fill="currentColor" text-anchor="middle" font-size="11">Waveform unavailable</text>';
    }
    const step = 200 / Math.max(1, samples.length - 1);
    const points = samples.map((sample, index) => {
      const x = (index * step).toFixed(2);
      const amplitude = Math.max(0, Math.min(1, Number(sample) || 0)) * 18;
      return `M${x} ${(20 - amplitude).toFixed(2)}V${(20 + amplitude).toFixed(2)}`;
    }).join("");
    return `<path d="${points}" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" />`;
  }

  async _loadChimeSetWaveform(member) {
    if (!member || this._chimeSetWaveformCache.has(member)) return;
    const loadToken = ++this._chimeSetWaveformLoadToken;
    try {
      const response = await this._fetchPickerWithAuth(this._buildChimePreviewUrl("chime_path", member));
      if (!response.ok) throw new Error(`Chime waveform request failed with status ${response.status}`);
      const audioData = await response.arrayBuffer();
      const AudioContextConstructor = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextConstructor) throw new Error("Web Audio is unavailable");
      this._chimeSetWaveformAudioContext ||= new AudioContextConstructor();
      const audioBuffer = await this._chimeSetWaveformAudioContext.decodeAudioData(audioData.slice(0));
      const samples = this._extractChimeSetWaveformSamples(audioBuffer);
      this._chimeSetWaveformCache.set(member, samples);
      this._chimeSetDurationCache.set(member, audioBuffer.duration * 1000);
      if (loadToken !== this._chimeSetWaveformLoadToken || this._chimeSetOffsetEditor?.member !== member) return;
      this._chimeSetOffsetEditor.waveform = samples;
      this._chimeSetOffsetEditor.chimeDuration = audioBuffer.duration * 1000;
      this._chimeSetOffsetEditor.timelineReady = true;
      this._render();
    } catch (_error) {
      // Keep the offset editor usable when a browser cannot decode a source format.
      this._chimeSetWaveformCache.set(member, []);
      if (loadToken !== this._chimeSetWaveformLoadToken || this._chimeSetOffsetEditor?.member !== member) return;
      this._chimeSetOffsetEditor.waveform = [];
      this._chimeSetOffsetEditor.timelineReady = true;
      this._render();
    }
  }

  _extractChimeSetWaveformSamples(audioBuffer) {
    const sampleCount = 96;
    const samples = Array(sampleCount).fill(0);
    const bucketSize = Math.max(1, Math.ceil(audioBuffer.length / sampleCount));
    for (let channel = 0; channel < audioBuffer.numberOfChannels; channel += 1) {
      const channelData = audioBuffer.getChannelData(channel);
      for (let bucket = 0; bucket < sampleCount; bucket += 1) {
        const start = bucket * bucketSize;
        const end = Math.min(channelData.length, start + bucketSize);
        const stride = Math.max(1, Math.floor((end - start) / 80));
        for (let index = start; index < end; index += stride) {
          samples[bucket] = Math.max(samples[bucket], Math.abs(channelData[index]));
        }
      }
    }
    const peak = Math.max(...samples, 0.01);
    return samples.map((sample) => sample / peak);
  }

  _setChimeSetOffsetEditorValue(value, { syncInput = true } = {}) {
    if (!this._chimeSetOffsetEditor) return;
    const requestedOffset = String(value).trim() === "" ? Number.NaN : Number(value);
    const chimeDuration = Number(this._chimeSetOffsetEditor.chimeDuration) || 1000;
    const offset = Number.isFinite(requestedOffset)
      ? Math.max(-chimeDuration, requestedOffset)
      : requestedOffset;
    this._chimeSetOffsetEditor.offset = Number.isFinite(offset) ? String(Math.round(offset)) : String(value);
    if (!Number.isFinite(offset)) return;
    this._stopChimeSetOffsetPreview();
    const timeline = this.shadowRoot.querySelector("[data-chime-set-offset-timeline]");
    const resetButton = this.shadowRoot.querySelector("[data-chime-set-offset-reset]");
    const closeButton = this.shadowRoot.querySelector("[data-chime-set-offset-close]");
    const valueButton = this.shadowRoot.querySelector("[data-chime-set-offset-value]");
    const valueInput = this.shadowRoot.querySelector("[data-chime-set-offset-input]");
    const changed = Number(this._chimeSetOffsetEditor.offset)
      !== Number(this._chimeSetOffsetEditor.initialOffset);
    if (resetButton) {
      resetButton.disabled = !changed;
    }
    if (closeButton) closeButton.textContent = changed ? "Done" : this._t("action.close");
    if (valueButton) valueButton.textContent = `${this._chimeSetOffsetEditor.offset} ms`;
    if (valueInput && syncInput) {
      const editorValue = this._chimeSetOffsetEditor.offset;
      // Keep the live number control in sync after dragging. Updating its
      // default value too prevents a previous manual edit from retaining a
      // stale browser-controlled value.
      valueInput.value = editorValue;
      valueInput.defaultValue = editorValue;
      valueInput.setAttribute("value", editorValue);
      valueInput.setCustomValidity("");
    }
    if (timeline) this._positionChimeSetOffsetTimeline(timeline);
  }

  _resetChimeSetOffsetEditor() {
    if (!this._chimeSetOffsetEditor) return;
    this._setChimeSetOffsetEditorValue(this._chimeSetOffsetEditor.initialOffset);
    const input = this.shadowRoot?.querySelector("[data-chime-set-offset-input]");
    if (input) {
      input.value = this._chimeSetOffsetEditor.offset;
      input.setCustomValidity("");
    }
  }

  _editChimeSetOffsetValue() {
    if (!this._chimeSetOffsetEditor) return;
    this._chimeSetOffsetEditor.editingOffset = true;
    this._render();
    this.shadowRoot?.querySelector("[data-chime-set-offset-input]")?.focus();
  }

  _handleChimeSetOffsetInput(event) {
    const input = event.currentTarget;
    const value = String(input.value).trim();
    const offset = Number(value);
    const isValid = value !== "" && Number.isFinite(offset) && Number.isInteger(offset);
    input.setCustomValidity(isValid ? "" : "Enter a whole number of milliseconds.");
    if (!isValid) return;
    // Do not write to the input while its own input event is being handled.
    // Drag and keyboard updates still synchronize it through the default path.
    this._setChimeSetOffsetEditorValue(offset, { syncInput: false });
  }

  _positionChimeSetOffsetTimeline(timeline) {
    if (!timeline) return;
    const offset = Number(this._chimeSetOffsetEditor?.offset);
    if (!Number.isFinite(offset)) return;
    const width = timeline.clientWidth;
    if (!width) return;

    // The TTS block begins at the end of the chime at zero. A positive offset
    // adds a gap; a negative one moves it back over (or before) the chime.
    const chimeWidth = Math.max(1, Number(this._chimeSetOffsetEditor?.chimeDuration) || 1000);
    const ttsWidth = 1560;
    const ttsStart = chimeWidth + offset;
    const contentStart = Math.min(0, ttsStart);
    const contentEnd = Math.max(chimeWidth, ttsStart + ttsWidth);
    const contentWidth = Math.max(1, contentEnd - contentStart);
    const scale = width / contentWidth;
    const left = -(contentStart * scale);
    const axis = timeline.parentElement?.querySelector("[data-chime-set-offset-axis]");
    if (axis) {
      const minimumTick = 10;
      const intervals = [];
      for (let magnitude = minimumTick; magnitude <= contentWidth * 10; magnitude *= 10) {
        [1, 2, 5].forEach((multiplier) => intervals.push(multiplier * magnitude));
      }
      const tickOptions = intervals.map((interval) => {
        const firstTick = Math.ceil(contentStart / interval) * interval;
        return {
          interval,
          firstTick,
          count: Math.floor((contentEnd - firstTick) / interval) + 1,
        };
      }).filter((option) => option.count > 0);
      const targetTickCount = 8;
      const matchingOptions = tickOptions.filter((option) => option.count >= 7 && option.count <= 10);
      const selectedOption = (matchingOptions.length ? matchingOptions : tickOptions)
        .sort((leftOption, rightOption) => (
          Math.abs(leftOption.count - targetTickCount) - Math.abs(rightOption.count - targetTickCount)
        ))[0];
      const { interval, firstTick } = selectedOption;
      const ticks = [];
      for (let tick = firstTick; tick <= contentEnd; tick += interval) {
        const position = (tick - contentStart) * scale;
        ticks.push({ value: Math.round(tick / 10) * 10, position });
      }
      axis.innerHTML = ticks.map(({ value, position }) => (
        `<span class="chime-set-offset-axis-label" style="left:${position}px">${value} ms</span>`
      )).join("");
      timeline.querySelectorAll("[data-chime-set-offset-grid]").forEach((line) => line.remove());
      ticks.forEach(({ position }) => {
        const line = document.createElement("span");
        line.className = "chime-set-offset-grid-line";
        line.dataset.chimeSetOffsetGrid = "1";
        line.style.left = `${position}px`;
        timeline.prepend(line);
      });
    }
    const chime = timeline.querySelector('[data-chime-set-offset-audio="chime"]');
    const tts = timeline.querySelector('[data-chime-set-offset-audio="tts"]');

    if (chime) {
      chime.style.left = `${left}px`;
      chime.style.width = `${chimeWidth * scale}px`;
      chime.setAttribute("aria-valuenow", String(offset));
    }
    if (tts) {
      tts.style.left = `${left + (ttsStart * scale)}px`;
      tts.style.width = `${ttsWidth * scale}px`;
      tts.setAttribute("aria-valuenow", String(offset));
    }
    const chimeStart = left;
    const chimeEnd = left + (chimeWidth * scale);
    const ttsStartPosition = left + (ttsStart * scale);
    const ttsEndPosition = ttsStartPosition + (ttsWidth * scale);
    const overlapLines = {
      start: ttsStartPosition > chimeStart && ttsStartPosition < chimeEnd ? ttsStartPosition : null,
      end: ttsEndPosition > chimeStart && ttsEndPosition < chimeEnd ? ttsEndPosition : null,
    };
    timeline.querySelectorAll("[data-chime-set-offset-overlap]").forEach((line) => {
      const position = overlapLines[line.dataset.chimeSetOffsetOverlap];
      line.style.display = position === null ? "none" : "block";
      if (position !== null) line.style.left = `${position}px`;
    });
  }

  _startChimeSetOffsetDrag(event) {
    if (event.button !== 0 || !this._chimeSetOffsetEditor) return;
    event.preventDefault();
    const audio = event.currentTarget;
    const timeline = audio.closest("[data-chime-set-offset-timeline]");
    const initialOffset = Number(this._chimeSetOffsetEditor.offset);
    if (!timeline || !Number.isFinite(initialOffset)) return;
    const direction = audio.dataset.chimeSetOffsetAudio === "chime" ? -1 : 1;
    const startX = event.clientX;
    timeline.classList.add("dragging");
    audio.setPointerCapture?.(event.pointerId);
    const onMove = (moveEvent) => {
      if (moveEvent.pointerId !== event.pointerId) return;
      this._setChimeSetOffsetEditorValue(initialOffset + (Math.round(moveEvent.clientX - startX) * direction * 10));
    };
    const onEnd = (endEvent) => {
      if (endEvent.pointerId !== event.pointerId) return;
      audio.removeEventListener("pointermove", onMove);
      audio.removeEventListener("pointerup", onEnd);
      audio.removeEventListener("pointercancel", onEnd);
      timeline.classList.remove("dragging");
    };
    audio.addEventListener("pointermove", onMove);
    audio.addEventListener("pointerup", onEnd);
    audio.addEventListener("pointercancel", onEnd);
  }

  _handleChimeSetOffsetAudioKeydown(event) {
    if (!this._chimeSetOffsetEditor || !["ArrowLeft", "ArrowRight"].includes(event.key)) return;
    event.preventDefault();
    const direction = event.key === "ArrowRight" ? 1 : -1;
    const audioDirection = event.currentTarget.dataset.chimeSetOffsetAudio === "chime" ? -1 : 1;
    const step = event.shiftKey ? 100 : 10;
    this._setChimeSetOffsetEditorValue(Number(this._chimeSetOffsetEditor.offset) + (direction * audioDirection * step));
  }

  _closeChimeSetOffsetEditor() {
    this._saveChimeSetOffset();
  }

  _saveChimeSetOffset() {
    const editor = this._chimeSetOffsetEditor;
    const offset = Number(editor?.offset);
    if (!editor || !Number.isInteger(offset)) return;
    if (editor.kind === "chime") {
      this._chimeSetOffsetEditor = null;
      this._stopChimeSetOffsetPreview();
      this._draftValues = {
        ...(this._draftValues || {}),
        chime_offsets: { ...(this._draftValues?.chime_offsets || {}), [editor.member]: offset },
      };
      this._isDirty = this._hasValueChanges();
      this._rerenderPreservingInputState();
      return;
    }
    const sets = this._randomChimeSetsDraft();
    if (!sets[editor.index]) return;
    sets[editor.index].offsets = { ...(sets[editor.index].offsets || {}), [editor.member]: offset };
    this._chimeSetOffsetEditor = null;
    this._stopChimeSetOffsetPreview();
    this._setRandomChimeSetsDraft(sets);
  }

  _buildChimeSetOffsetPreviewUrl(member, offset) {
    return `/api/chime_tts/chime_set_offset_preview?value=${encodeURIComponent(member)}&offset=${encodeURIComponent(offset)}`;
  }

  _stopChimeSetOffsetPreview() {
    this._chimeSetOffsetPreviewToken += 1;
    if (this._chimeSetOffsetPreviewAudio) {
      this._chimeSetOffsetPreviewAudio.pause();
      this._chimeSetOffsetPreviewAudio.src = "";
      this._chimeSetOffsetPreviewAudio.load();
      this._chimeSetOffsetPreviewAudio = null;
    }
    if (this._chimeSetOffsetPreviewObjectUrl) URL.revokeObjectURL(this._chimeSetOffsetPreviewObjectUrl);
    this._chimeSetOffsetPreviewObjectUrl = "";
    if (this._chimeSetOffsetEditor) {
      this._chimeSetOffsetEditor.previewPlaying = false;
      this._chimeSetOffsetEditor.previewStarted = false;
    }
    const button = this.shadowRoot?.querySelector("[data-chime-set-offset-preview]");
    if (button) {
      button.classList.remove("stop");
      button.innerHTML = `${ICONS.play}<span>Preview</span>`;
    }
    const playbackHead = this.shadowRoot?.querySelector(".chime-set-offset-playback-head");
    if (playbackHead) playbackHead.classList.remove("playing");
  }

  async _toggleChimeSetOffsetPreview() {
    const editor = this._chimeSetOffsetEditor;
    if (!editor) return;
    if (editor.previewPlaying) {
      this._stopChimeSetOffsetPreview();
      this._render();
      return;
    }
    const token = ++this._chimeSetOffsetPreviewToken;
    editor.previewPlaying = true;
    editor.previewStarted = false;
    this._render();
    try {
      const objectUrl = await this._fetchPickerAudioObjectUrl(this._buildChimeSetOffsetPreviewUrl(editor.member, editor.offset));
      if (token !== this._chimeSetOffsetPreviewToken) {
        URL.revokeObjectURL(objectUrl);
        return;
      }
      const audio = new Audio(objectUrl);
      this._chimeSetOffsetPreviewAudio = audio;
      this._chimeSetOffsetPreviewObjectUrl = objectUrl;
      audio.addEventListener("loadedmetadata", () => {
        if (this._chimeSetOffsetPreviewAudio === audio && this._chimeSetOffsetEditor) {
          this._chimeSetOffsetEditor.previewDuration = audio.duration;
          this._render();
        }
      });
      audio.addEventListener("play", () => {
        if (this._chimeSetOffsetPreviewAudio === audio && this._chimeSetOffsetEditor) {
          this._chimeSetOffsetEditor.previewStarted = true;
          this._render();
        }
      });
      audio.addEventListener("ended", () => {
        if (this._chimeSetOffsetPreviewAudio === audio) {
          this._stopChimeSetOffsetPreview();
          this._render();
        }
      });
      await audio.play();
    } catch (_error) {
      if (token === this._chimeSetOffsetPreviewToken) {
        this._stopChimeSetOffsetPreview();
        this._render();
      }
    }
  }

  _requestRandomChimeSetDelete(index) {
    const sets = this._randomChimeSetsDraft();
    const chimeSet = sets[index];
    if (!chimeSet) return;
    const savedSetIds = new Set(
      (this._data?.values?.chime_sets || []).map((set) => set?.id).filter(Boolean),
    );
    if (!savedSetIds.has(chimeSet.id)) {
      this._deleteRandomChimeSet(index);
      return;
    }
    const reference = String(chimeSet.name || "").trim();
    const usedBy = [];
    for (const field of ["chime_path", "end_chime_path"]) {
      if (this._draftValues?.[field] === reference && !usedBy.includes("default settings")) usedBy.push("default settings");
    }
    (this._draftNotifyProfiles || []).forEach((profile) => {
      for (const field of ["chime_path", "end_chime_path"]) {
        if (profile?.[field] === reference) {
          const profileName = String(profile?.name || "").trim() || "Unnamed notification profile";
          if (!usedBy.includes(profileName)) usedBy.push(`"${profileName}" notification profile`);
        }
      }
    });
    this._randomChimeSetDeleteTarget = { index, name: chimeSet.name, usedBy };
    this._render();
  }

  _deleteRandomChimeSet(index) {
    const sets = this._randomChimeSetsDraft();
    if (!sets[index]) {
      return;
    }
    sets.splice(index, 1);
    this._expandedRandomChimeSets = this._reindexNotifyProfileState(this._expandedRandomChimeSets, index);
    this._randomChimeSetDeleteTarget = null;
    this._setRandomChimeSetsDraft(sets);
  }

  _closeRandomChimeSetDeleteConfirmation() {
    this._randomChimeSetDeleteTarget = null;
    this._render();
  }

  _confirmRandomChimeSetDelete() {
    const index = this._randomChimeSetDeleteTarget?.index;
    if (!Number.isInteger(index)) {
      this._closeRandomChimeSetDeleteConfirmation();
      return;
    }
    this._deleteRandomChimeSet(index);
  }

  _isRandomChimeSetExpanded(index) {
    return this._expandedRandomChimeSets?.[index] === true;
  }

  _toggleRandomChimeSet(index) {
    if (Number.isNaN(index)) return;
    const expanded = !this._isRandomChimeSetExpanded(index);
    this._expandedRandomChimeSets = {
      ...(this._expandedRandomChimeSets || {}),
      [index]: expanded,
    };
    const card = this.shadowRoot?.querySelector(
      `[data-random-chime-set-card="${this._escapeSelectorValue(index)}"]`,
    );
    this._applyExpandableState(card, expanded, {
      buttonSelector: "[data-toggle-random-chime-set]",
      labelType: "Chime Set",
    });
  }

  _handleNotifyProfileFieldChange(event) {
    const field = event.currentTarget;
    const key = field?.dataset?.notifyField;
    const index = Number(field?.dataset?.notifyIndex);
    if (!key || Number.isNaN(index)) {
      return;
    }

    const nextValue = field.type === "checkbox" ? field.checked : field.value;
    const nextProfiles = this._cloneNotifyProfiles(this._draftNotifyProfiles || []);
    if (!nextProfiles[index]) {
      return;
    }
    nextProfiles[index] = {
      ...nextProfiles[index],
      [key]: nextValue,
    };
    this._draftNotifyProfiles = nextProfiles;

    if (this._notifyProfileClientErrors?.[index]?.[key]) {
      const nextErrors = this._cloneNotifyProfileErrors(this._notifyProfileClientErrors);
      delete nextErrors[index][key];
      this._notifyProfileClientErrors = nextErrors;
    }

    this._isDirty = this._hasValueChanges();
    this._rerenderPreservingInputState();
  }

  _handleNotifyRangeInput(event) {
    const field = event.currentTarget;
    const key = field?.dataset?.notifyRange;
    const index = Number(field?.dataset?.notifyIndex);
    if (!key || Number.isNaN(index)) {
      return;
    }
    this._setNotifyRangeDraftValue(index, key, field.value, { rerender: false });
    this._syncNotifyRangeRow(index, key, field.value);
    this._renderTopbar(this._data || {});
  }

  _handleNotifyRangeCommit(event) {
    const field = event.currentTarget;
    const key = field?.dataset?.notifyRange;
    const index = Number(field?.dataset?.notifyIndex);
    if (!key || Number.isNaN(index)) {
      return;
    }
    this._setNotifyRangeDraftValue(index, key, field.value, { rerender: true });
  }

  _handleNotifyRangeNumberInput(event) {
    const field = event.currentTarget;
    const key = field?.dataset?.notifyRangeNumber;
    const index = Number(field?.dataset?.notifyIndex);
    if (!key || Number.isNaN(index)) {
      return;
    }
    this._setNotifyRangeDraftValue(index, key, field.value, { rerender: false, allowPartial: true });
    this._syncNotifyRangeRow(index, key, field.value);
    this._renderTopbar(this._data || {});
  }

  _handleNotifyRangeNumberCommit(event) {
    const field = event.currentTarget;
    const key = field?.dataset?.notifyRangeNumber;
    const index = Number(field?.dataset?.notifyIndex);
    if (!key || Number.isNaN(index)) {
      return;
    }
    const normalized = this._normalizeNotifyRangeValue(index, key, field.value);
    this._setNotifyRangeDraftValue(index, key, normalized, { rerender: true });
  }

  _setNotifyRangeDraftValue(index, key, nextValue, { rerender, allowPartial = false }) {
    const nextProfiles = this._cloneNotifyProfiles(this._draftNotifyProfiles || []);
    if (!nextProfiles[index]) {
      return;
    }
    const normalizedValue = allowPartial ? nextValue : this._normalizeNotifyRangeValue(index, key, nextValue);
    nextProfiles[index] = {
      ...nextProfiles[index],
      [key]: normalizedValue,
    };
    this._draftNotifyProfiles = nextProfiles;
    if (this._notifyProfileClientErrors?.[index]?.[key]) {
      const nextErrors = this._cloneNotifyProfileErrors(this._notifyProfileClientErrors);
      delete nextErrors[index][key];
      this._notifyProfileClientErrors = nextErrors;
    }
    this._isDirty = this._hasValueChanges();
    if (rerender) {
      this._rerenderPreservingInputState();
    }
  }

  _normalizeNotifyRangeValue(index, key, rawValue) {
    const field = this._findNotifyProfileField(key);
    if (!field) {
      return rawValue;
    }
    const savedValue = this._data?.notify_profiles?.[index]?.[key] ?? "";
    if (rawValue === "" || rawValue === null || rawValue === undefined) {
      return savedValue === "" ? "" : savedValue;
    }
    const numeric = Number(rawValue);
    if (Number.isNaN(numeric)) {
      return savedValue;
    }
    const min = Number(field.min ?? numeric);
    const max = Number(field.max ?? numeric);
    const step = Number(field.step ?? 1);
    const clamped = Math.min(max, Math.max(min, numeric));
    const stepped = Math.round(clamped / step) * step;
    return Number(step < 1 ? stepped.toFixed(2) : stepped);
  }

  _syncNotifyRangeRow(index, key, rawValue) {
    const field = this._findNotifyProfileField(key);
    const value = rawValue === "" || rawValue === null || rawValue === undefined
      ? ""
      : String(rawValue);
    const rangeInput = this.shadowRoot.querySelector(`[data-notify-range="${CSS.escape(key)}"][data-notify-index="${CSS.escape(String(index))}"]`);
    const numberInput = this.shadowRoot.querySelector(`[data-notify-range-number="${CSS.escape(key)}"][data-notify-index="${CSS.escape(String(index))}"]`);
    if (rangeInput) {
      rangeInput.value = value !== "" && !Number.isNaN(Number(value))
        ? value
        : String(field?.min ?? 0);
      this._updateNotifyRangeProgress(rangeInput);
    }
    if (numberInput && document.activeElement !== numberInput) {
      numberInput.value = value;
      numberInput.placeholder = value === ""
        ? this._t("placeholder.auto", { unit: field?.unit ? ` ${field.unit}` : "" })
        : "";
    }
  }

  _updateNotifyRangeProgress(rangeInput) {
    const min = Number(rangeInput?.min);
    const max = Number(rangeInput?.max);
    const value = Number(rangeInput?.value);
    const progress = Number.isFinite(min) && Number.isFinite(max) && max !== min && Number.isFinite(value)
      ? Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100))
      : 0;
    rangeInput?.style.setProperty("--range-progress", `${progress}%`);
  }

  _resetNotifyProfileField(index, key) {
    if (!key || Number.isNaN(index)) {
      return;
    }
    const savedValue = this._data?.notify_profiles?.[index]?.[key];
    const nextProfiles = this._cloneNotifyProfiles(this._draftNotifyProfiles || []);
    if (!nextProfiles[index]) {
      return;
    }
    nextProfiles[index] = {
      ...nextProfiles[index],
      [key]: savedValue ?? "",
    };
    this._draftNotifyProfiles = nextProfiles;
    this._isDirty = this._hasValueChanges();
    this._render();
  }

  _resetNotifyProfile(index) {
    if (Number.isNaN(index)) {
      return;
    }
    const savedProfile = (this._data?.notify_profiles || [])[index];
    if (!savedProfile) {
      this._removeNotifyProfile(index);
      return;
    }
    const profiles = this._cloneNotifyProfiles(this._draftNotifyProfiles || []);
    profiles[index] = this._cloneNotifyProfiles([savedProfile])[0];
    this._draftNotifyProfiles = profiles;
    const errors = this._cloneNotifyProfileErrors(this._notifyProfileClientErrors);
    errors[index] = {};
    this._notifyProfileClientErrors = errors;
    this._notifyProfileTests = {
      ...(this._notifyProfileTests || {}),
      [index]: { open: false, message: "", sending: false, sentAt: 0 },
    };
    this._isDirty = this._hasValueChanges();
    this._render();
  }

  _addNotifyProfile() {
    const defaults = this._buildEmptyNotifyProfile();
    this._draftNotifyProfiles = [defaults, ...(this._draftNotifyProfiles || [])];
    this._notifyProfileClientErrors = [{}, ...(this._notifyProfileClientErrors || [])];
    this._expandedNotifyProfiles = {
      ...this._offsetNotifyProfileState(this._expandedNotifyProfiles, 1),
      0: true,
    };
    this._notifyProfileTests = this._offsetNotifyProfileState(this._notifyProfileTests, 1);
    this._isDirty = this._hasValueChanges();
    this._render();
  }

  _removeNotifyProfile(index) {
    if (Number.isNaN(index)) {
      return;
    }
    this._draftNotifyProfiles = (this._draftNotifyProfiles || []).filter((_, itemIndex) => itemIndex !== index);
    this._notifyProfileClientErrors = (this._notifyProfileClientErrors || []).filter((_, itemIndex) => itemIndex !== index);
    this._expandedNotifyProfiles = this._reindexNotifyProfileState(this._expandedNotifyProfiles, index);
    this._notifyProfileTests = this._reindexNotifyProfileState(this._notifyProfileTests, index);
    this._isDirty = this._hasValueChanges();
    this._renderPreservingScrollPosition();
  }

  _toggleNotifyProfile(index) {
    if (Number.isNaN(index)) {
      return;
    }
    this._animateHeightTransition(
      `[data-notify-profile-card="${this._escapeSelectorValue(String(index))}"]`,
      () => {
        const expanded = !this._isNotifyProfileExpanded(index);
        this._expandedNotifyProfiles = {
          ...(this._expandedNotifyProfiles || {}),
          [index]: expanded,
        };
        this._render();
      },
    );
  }

  _shouldIgnoreNotifyProfileCardToggle(event) {
    const target = event.target;
    if (!(target instanceof Element)) {
      return false;
    }

    if (event.type === "click" && window.getSelection && !window.getSelection().isCollapsed) {
      return true;
    }

    return Boolean(
      target.closest(
        [
          "a",
          "button",
          "input",
          "select",
          "textarea",
          "label",
          "ha-entity-picker",
          ".notify-profile-actions",
          ".row-collapse",
          ".notify-entity-chip-list",
        ].join(", "),
      ),
    );
  }

  _isNotifyProfileExpanded(index) {
    const explicit = this._expandedNotifyProfiles?.[index];
    return explicit === true;
  }

  _escapeSelectorValue(value) {
    const text = String(value ?? "");
    if (globalThis.CSS?.escape) {
      return globalThis.CSS.escape(text);
    }
    return text.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  }

  _applyExpandableState(element, expanded, { buttonSelector = null, labelType = "row" } = {}) {
    if (!element) {
      return;
    }

    element.classList.toggle("expanded", expanded);
    element.classList.toggle("collapsed", !expanded);
    element.setAttribute("aria-expanded", expanded ? "true" : "false");

    const collapse = element.querySelector(":scope > .row-collapse");
    if (collapse) {
      collapse.classList.toggle("expanded", expanded);
      collapse.classList.toggle("collapsed", !expanded);
    }

    const buttons = buttonSelector ? element.querySelectorAll(buttonSelector) : [];
    buttons.forEach((button) => {
      button.classList.toggle("expanded", expanded);
      button.classList.toggle("collapsed", !expanded);
      button.setAttribute("aria-label", this._t(expanded ? "aria.collapse_named" : "aria.expand_named", { title: labelType }));
      button.setAttribute("title", this._t(expanded ? "action.collapse" : "action.expand"));
      button.setAttribute("aria-expanded", expanded ? "true" : "false");
    });
  }

  _applyAdvancedSectionState(sectionKey, expanded) {
    const section = this.shadowRoot?.querySelector(
      `[data-section-key="${this._escapeSelectorValue(sectionKey)}"]`,
    );
    if (!section) {
      return;
    }

    const button = section.querySelector(
      `[data-toggle-advanced="${this._escapeSelectorValue(sectionKey)}"]`,
    );
    if (button) {
      button.textContent = `${expanded ? "Hide" : "Show"} Advanced`;
    }

    const collapses = section.querySelectorAll(":scope .row-collapse");
    const advancedCollapse = collapses.length > 1 ? collapses[1] : null;
    if (advancedCollapse) {
      advancedCollapse.classList.toggle("expanded", expanded);
      advancedCollapse.classList.toggle("collapsed", !expanded);
    }
  }

  _applyChapterState(chapterKey, expanded) {
    const group = this.shadowRoot?.querySelector(
      `[data-chapter-key="${this._escapeSelectorValue(chapterKey)}"]`,
    );
    if (!group) {
      return;
    }

    group.classList.toggle("expanded", expanded);
    group.classList.toggle("collapsed", !expanded);

    const toggle = group.querySelector(
      `[data-toggle-chapter="${this._escapeSelectorValue(chapterKey)}"]`,
    );
    if (toggle) {
      toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
      const title = group.querySelector(".chapter-hero-title")?.textContent?.trim() || "section";
      toggle.setAttribute("aria-label", this._t(expanded ? "aria.collapse_named" : "aria.expand_named", { title }));
    }

    const collapse = group.querySelector(":scope .chapter-collapse");
    if (collapse) {
      collapse.classList.toggle("expanded", expanded);
      collapse.classList.toggle("collapsed", !expanded);
    }
  }

  _animateHeightTransition(selector, mutate) {
    const beforeElement = this.shadowRoot?.querySelector(selector);
    const startHeight = beforeElement?.getBoundingClientRect().height ?? null;
    mutate();
    if (startHeight === null) {
      return;
    }
    const afterElement = this.shadowRoot?.querySelector(selector);
    if (!afterElement) {
      return;
    }
    const endHeight = afterElement.getBoundingClientRect().height;
    if (Math.abs(endHeight - startHeight) < 1) {
      return;
    }

    afterElement.style.height = `${startHeight}px`;
    afterElement.style.overflow = "hidden";
    afterElement.style.transition = "height 250ms ease";
    afterElement.getBoundingClientRect();

    requestAnimationFrame(() => {
      afterElement.style.height = `${endHeight}px`;
    });

    const cleanup = () => {
      afterElement.style.height = "";
      afterElement.style.overflow = "";
      afterElement.style.transition = "";
    };

    afterElement.addEventListener("transitionend", cleanup, { once: true });
    window.setTimeout(cleanup, 300);
  }

  _notifyTargets(profile) {
    if (Array.isArray(profile?.targets) && profile.targets.length > 0) {
      return profile.targets.filter((target) => target?.type && target?.id);
    }
    return String(profile?.entity_id || "").split(",").map((id) => id.trim()).filter(Boolean)
      .map((id) => ({ type: "entity_id", id }));
  }

  _notifyTargetLabel(type) {
    return ({ entity_id: "Entity", device_id: "Device", area_id: "Area", floor_id: "Floor", label_id: "Label" })[type] || type;
  }

  _removeNotifyEntity(index, encodedTarget) {
    if (Number.isNaN(index) || !encodedTarget) {
      return;
    }
    const [type, ...idParts] = encodedTarget.split(":");
    const id = idParts.join(":");
    const nextProfiles = this._cloneNotifyProfiles(this._draftNotifyProfiles || []);
    const targets = this._notifyTargets(nextProfiles[index]);
    nextProfiles[index] = {
      ...nextProfiles[index],
      targets: targets.filter((target) => target.type !== type || target.id !== id),
    };
    this._draftNotifyProfiles = nextProfiles;
    this._isDirty = this._hasValueChanges();
    this._render();
  }

  _wireNotifyEntityPickers() {
    this.shadowRoot.querySelectorAll("[data-notify-target-picker]").forEach((picker) => {
      const index = Number(picker.dataset.notifyTargetPicker);
      picker.hass = this._hass;
      picker.selector = { target: { entity: { domain: ["media_player"] } } };
      picker.value = {};
      picker.disabled = this._saving;
      this._applyNotifyTargetPickerAccent(picker);
      requestAnimationFrame(() => this._applyNotifyTargetPickerAccent(picker));
      requestAnimationFrame(() => requestAnimationFrame(() => this._applyNotifyTargetPickerAccent(picker)));
      window.setTimeout(() => this._applyNotifyTargetPickerAccent(picker), 50);
      picker.updateComplete?.then(() => this._applyNotifyTargetPickerAccent(picker));
      if (!picker.__notifyAccentObserver) {
        const observer = new MutationObserver(() => this._applyNotifyTargetPickerAccent(picker));
        observer.observe(picker, { childList: true, subtree: true });
        picker.__notifyAccentObserver = observer;
      }
      if (!picker.__notifyAccentStateListenersBound) {
        picker.__notifyAccentStateListenersBound = true;
        ["pointerover", "pointerdown", "focusin", "focusout", "keydown"].forEach((eventName) => {
          picker.addEventListener(eventName, () => this._applyNotifyTargetPickerAccent(picker), true);
        });
      }
      if (picker.__notifyPickerBound) {
        return;
      }
      picker.__notifyPickerBound = true;
      picker.addEventListener("value-changed", (event) => {
        const selected = event.detail?.value;
        if (!selected || typeof selected !== "object") {
          return;
        }
        Object.entries(selected).forEach(([type, ids]) => {
          if (["entity_id", "device_id", "area_id", "floor_id", "label_id"].includes(type)) {
            (Array.isArray(ids) ? ids : [ids]).forEach((id) => this._addNotifyEntity(index, { type, id }));
          }
        });
        picker.value = {};
      });
    });
  }

  _applyNotifyTargetPickerAccent(picker) {
    const buttons = new Set();
    const roots = [picker, picker?.shadowRoot].filter(Boolean);
    while (roots.length > 0) {
      const root = roots.pop();
      root.querySelectorAll("ha-button").forEach((button) => buttons.add(button));
      root.querySelectorAll("*").forEach((element) => {
        if (element.shadowRoot) {
          roots.push(element.shadowRoot);
        }
      });
    }
    const accent = "var(--workspace-accent)";
    buttons.forEach((button) => {
      for (const property of [
        "--wa-color-fill-normal",
        "--wa-color-fill-loud",
        "--wa-color-brand-fill-normal",
        "--wa-color-brand-fill-loud",
        "--button-color-fill-normal-hover",
        "--button-color-fill-normal-active",
        "--button-color-fill-loud-hover",
        "--button-color-fill-loud-active",
      ]) {
        button.style.setProperty(property, accent);
      }
      button.style.setProperty("--wa-color-on-normal", "#fff");
      button.style.setProperty("--wa-color-on-loud", "#fff");
      button.style.setProperty("--wa-color-brand-on-normal", "#fff");
      button.style.setProperty("--wa-color-brand-on-loud", "#fff");
      button.style.setProperty("--ha-color-on-primary-normal", "#fff");
      button.style.setProperty("--ha-color-on-primary-loud", "#fff");
      button.style.setProperty("--mdc-theme-on-primary", "#fff");
      button.style.setProperty("color", "#fff", "important");
      const buttonRoots = [button, button.shadowRoot].filter(Boolean);
      while (buttonRoots.length > 0) {
        const root = buttonRoots.pop();
        root.querySelectorAll("*").forEach((element) => {
          if (element instanceof HTMLElement || element instanceof SVGElement) {
            element.style.setProperty("color", "#fff", "important");
            element.style.setProperty("fill", "#fff", "important");
            element.style.setProperty("stroke", "#fff", "important");
          }
          if (element.shadowRoot) buttonRoots.push(element.shadowRoot);
        });
      }
    });
  }

  _syncLiveHassBindings() {
    if (!this.shadowRoot) {
      return;
    }
    this._wireNotifyEntityPickers();
  }

  _addNotifyEntity(index, target) {
    if (Number.isNaN(index) || !target?.type || !target?.id) {
      return;
    }
    const nextProfiles = this._cloneNotifyProfiles(this._draftNotifyProfiles || []);
    const targets = this._notifyTargets(nextProfiles[index]);
    if (!targets.some((item) => item.type === target.type && item.id === target.id)) {
      targets.push({ type: target.type, id: target.id });
    }
    nextProfiles[index] = {
      ...nextProfiles[index],
      targets,
    };
    this._draftNotifyProfiles = nextProfiles;
    if (this._notifyProfileClientErrors?.[index]?.targets) {
      const nextErrors = this._cloneNotifyProfileErrors(this._notifyProfileClientErrors);
      delete nextErrors[index].targets;
      this._notifyProfileClientErrors = nextErrors;
    }
    this._isDirty = this._hasValueChanges();
    this._render();
  }

  _reindexNotifyProfileState(state, removedIndex) {
    const nextState = {};
    for (const [key, value] of Object.entries(state || {})) {
      const index = Number(key);
      if (Number.isNaN(index) || index === removedIndex) {
        continue;
      }
      nextState[index > removedIndex ? index - 1 : index] = value;
    }
    return nextState;
  }

  _offsetNotifyProfileState(state, offset) {
    const nextState = {};
    for (const [key, value] of Object.entries(state || {})) {
      const index = Number(key);
      if (Number.isNaN(index)) {
        continue;
      }
      nextState[index + offset] = value;
    }
    return nextState;
  }

  async _openPicker(fieldKey) {
    if (!fieldKey || this._pickerLoading) {
      return;
    }
    this._pickerFilter = "";
    this._pickerBusy = false;
    this._pickerAction = null;
    this._pickerMenuOpen = false;
    this._picker = {
      field_key: fieldKey,
      title: this._findFieldLabel(fieldKey),
      requested_path: this._draftValues?.[fieldKey] || "",
      requested_path_exists: true,
      requested_path_missing: false,
      selected_path_notice: "",
      current_path: this._draftValues?.[fieldKey] || "",
      parent_path: null,
      items: [],
      roots: [],
      directories: [],
    };
    this._pickerSelectedPath = this._draftValues?.[fieldKey] || "";
    this._pickerError = null;
    this._pickerLoading = true;
    this._pickerNativeFileDialogOpen = false;
    this._beginPickerLoadingDelay();
    this._render();
    await this._loadPicker(this._draftValues?.[fieldKey] || "", fieldKey, { skipInitialRender: true });
  }

  _closePicker() {
    const fieldKey = this._picker?.field_key;
    this._stopPickerAudio();
    this._endPickerLoadingDelay();
    this._picker = null;
    this._pickerLoading = false;
    this._pickerNativeFileDialogOpen = false;
    this._pickerError = null;
    this._pickerBusy = false;
    this._pickerFilter = "";
    this._pickerSelectedPath = "";
    this._pickerAction = null;
    this._pickerMenuOpen = false;
    const flushedDeferredLogEvents = this._flushDeferredLogEvents();
    if (fieldKey === "custom_chimes_path") {
      this._refreshCustomChimesAfterPickerClose();
    }
    if (flushedDeferredLogEvents) {
      return;
    }
    this._render();
  }

  async _refreshCustomChimesAfterPickerClose() {
    try {
      const result = await this._hass.callWS({ type: "chime_tts/refresh_custom_chimes" });
      if (Array.isArray(result?.log_events)) {
        this._data = { ...(this._data || {}), log_events: result.log_events };
      }
      if (await this._reloadSettingsMetadata()) {
        this._rerenderPreservingInputState();
      }
    } catch (_error) {
      // The interval monitor will retry shortly if an immediate refresh is unavailable.
    }
  }

  async _reloadSettingsMetadata() {
    try {
      const settings = await this._hass.callWS({ type: "chime_tts/get_settings" });
      if (!Array.isArray(settings?.sections)) {
        return false;
      }
      this._data = {
        ...(this._data || {}),
        sections: settings.sections,
        values: settings.values || this._data?.values || {},
        restart_required_field_keys: settings.restart_required_field_keys || [],
      };
      return true;
    } catch (_error) {
      return false;
    }
  }

  async _refreshSavedSettingsMetadata() {
    if (await this._reloadSettingsMetadata()) {
      if (!this._saving && !this._isDirty) {
        this._render();
      }
    }
  }

  async _loadPicker(path, fieldKey = null, { skipInitialRender = false } = {}) {
    const targetFieldKey = fieldKey || this._picker?.field_key;
    if (!targetFieldKey) {
      return;
    }

    this._stopPickerAudio();
    this._pickerLoading = true;
    this._beginPickerLoadingDelay();
    this._pickerError = null;
    this._pickerMenuOpen = false;
    if (!skipInitialRender) {
      this._render();
    }

    try {
      const pickerData = await this._hass.callWS({
        type: "chime_tts/browse_path",
        field_key: targetFieldKey,
        path,
      });
      this._picker = {
        ...(this._picker || {}),
        ...pickerData,
      };
      this._pickerSelectedPath = this._isPickerPathSelectable(this._pickerSelectedPath)
        ? this._pickerSelectedPath
        : this._picker.current_path || "";
    } catch (error) {
      this._pickerError = error?.message || this._t("error.browse_folders");
    } finally {
      this._pickerLoading = false;
      this._endPickerLoadingDelay();
      this._render();
    }
  }

  _beginPickerLoadingDelay() {
    this._pickerLoadingToken += 1;
    const token = this._pickerLoadingToken;
    if (this._pickerLoadingDelayTimer) {
      window.clearTimeout(this._pickerLoadingDelayTimer);
    }
    this._pickerLoadingVisible = false;
    this._pickerLoadingDelayTimer = window.setTimeout(() => {
      this._pickerLoadingDelayTimer = null;
      if (!this._pickerLoading || token !== this._pickerLoadingToken) {
        return;
      }
      this._pickerLoadingVisible = true;
      this._render();
    }, 1000);
  }

  _endPickerLoadingDelay() {
    if (this._pickerLoadingDelayTimer) {
      window.clearTimeout(this._pickerLoadingDelayTimer);
      this._pickerLoadingDelayTimer = null;
    }
    this._pickerLoadingVisible = false;
  }

  _stopPickerAudio({ preserveElement = false } = {}) {
    this._pickerAudioLoadToken += 1;
    this._pickerAudioLoadingPath = "";
    if (this._pickerAudio) {
      try {
        this._pickerAudio.pause();
      } catch (_error) {
        // Ignore pause failures from browser media state transitions.
      }
      if (!preserveElement) {
        this._pickerAudio.src = "";
        this._pickerAudio = null;
      }
    }
    if (this._pickerAudioObjectUrl) {
      URL.revokeObjectURL(this._pickerAudioObjectUrl);
      this._pickerAudioObjectUrl = "";
    }
    if (this._pickerPlayingPath) {
      this._pickerPlayingPath = "";
    }
    this._pickerPreviewDuration = 0;
  }

  _isChimePreviewField(field) {
    return Boolean(field && (field.key === "chime_path" || field.key === "end_chime_path"));
  }

  _getFieldPreviewKey(fieldKey, value) {
    return `${fieldKey || ""}:${value || ""}`;
  }

  _previewPlayingStyle(isPlaying, duration) {
    if (!isPlaying) return "";
    const seconds = Number.isFinite(duration) && duration > 0 ? duration : 1;
    return `style="--preview-duration: ${seconds}s"`;
  }

  _buildChimePreviewUrl(fieldKey, value) {
    return `/api/chime_tts/chime_preview?field_key=${encodeURIComponent(fieldKey)}&value=${encodeURIComponent(value)}`;
  }

  _getNotifyPreviewKey(index, fieldKey, value) {
    return `${Number.isNaN(index) ? "" : index}:${fieldKey || ""}:${value || ""}`;
  }

  _stopFieldPreviewAudio({ preserveElement = false } = {}) {
    this._previewRenderPending = true;
    this._fieldPreviewAudioLoadToken += 1;
    if (this._fieldPreviewAudio) {
      this._fieldPreviewAudio.pause();
      this._fieldPreviewAudio.src = "";
      this._fieldPreviewAudio.load();
      if (!preserveElement) {
        this._fieldPreviewAudio = null;
      }
    }
    this._fieldPreviewLoadingKey = "";
    if (this._fieldPreviewAudioObjectUrl) {
      URL.revokeObjectURL(this._fieldPreviewAudioObjectUrl);
      this._fieldPreviewAudioObjectUrl = "";
    }
    if (this._fieldPreviewPlayingKey) {
      this._fieldPreviewPlayingKey = "";
    }
    this._fieldPreviewDuration = 0;
  }

  async _toggleFieldPreviewAudio(fieldKey, value) {
    if (!fieldKey || !value) {
      return;
    }

    const previewKey = this._getFieldPreviewKey(fieldKey, value);
    if (this._fieldPreviewPlayingKey === previewKey && this._fieldPreviewAudio) {
      this._stopFieldPreviewAudio({ preserveElement: true });
      this._rerenderPreservingInputState(fieldKey);
      return;
    }

    this._stopFieldPreviewAudio();
    this._fieldPreviewLoadingKey = previewKey;
    this._rerenderPreservingInputState(fieldKey);

    const loadToken = this._fieldPreviewAudioLoadToken;
    let objectUrl = "";
    try {
      objectUrl = await this._fetchPickerAudioObjectUrl(this._buildChimePreviewUrl(fieldKey, value));
    } catch (_error) {
      if (loadToken === this._fieldPreviewAudioLoadToken) {
        this._fieldPreviewLoadingKey = "";
        this._data = {
          ...(this._data || {}),
          message: this._t("error.play_chime_preview"),
          message_type: "error",
        };
        this._rerenderPreservingInputState(fieldKey);
      }
      return;
    }

    if (loadToken !== this._fieldPreviewAudioLoadToken) {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
      return;
    }

    const audio = new Audio(objectUrl);
    audio.addEventListener("loadedmetadata", () => {
      if (this._fieldPreviewAudio === audio) {
        this._fieldPreviewDuration = audio.duration;
        this._rerenderPreservingInputState(fieldKey);
      }
    });
    audio.addEventListener("ended", () => {
      if (this._fieldPreviewAudio === audio) {
        this._stopFieldPreviewAudio();
        this._rerenderPreservingInputState(fieldKey);
      }
    });
    audio.addEventListener("pause", () => {
      if (this._fieldPreviewAudio === audio && audio.ended) {
        return;
      }
      if (this._fieldPreviewAudio === audio && this._fieldPreviewPlayingKey) {
        this._fieldPreviewPlayingKey = "";
        this._rerenderPreservingInputState(fieldKey);
      }
    });
    audio.addEventListener("play", () => {
      if (this._fieldPreviewAudio === audio) {
        this._fieldPreviewLoadingKey = "";
        this._fieldPreviewPlayingKey = previewKey;
        this._fieldPreviewDuration = audio.duration;
        this._rerenderPreservingInputState(fieldKey);
      }
    });
    this._fieldPreviewAudio = audio;
    this._fieldPreviewAudioObjectUrl = objectUrl;
    this._fieldPreviewLoadingKey = "";
    this._fieldPreviewPlayingKey = previewKey;
    const playAttempt = audio.play();
    if (playAttempt && typeof playAttempt.catch === "function") {
      playAttempt.then(() => {
        if (this._fieldPreviewAudio === audio && !audio.paused && !audio.ended) {
          this._fieldPreviewLoadingKey = "";
          this._fieldPreviewPlayingKey = previewKey;
          this._rerenderPreservingInputState(fieldKey);
        }
      });
      playAttempt.catch(() => {
        if (this._fieldPreviewAudio === audio) {
          this._stopFieldPreviewAudio();
          this._data = {
            ...(this._data || {}),
            message: this._t("error.play_chime_preview"),
            message_type: "error",
          };
          this._rerenderPreservingInputState(fieldKey);
        }
      });
    }
    this._rerenderPreservingInputState(fieldKey);
  }

  _stopNotifyPreviewAudio({ preserveElement = false } = {}) {
    this._previewRenderPending = true;
    this._notifyPreviewAudioLoadToken += 1;
    if (this._notifyPreviewAudio) {
      this._notifyPreviewAudio.pause();
      this._notifyPreviewAudio.src = "";
      this._notifyPreviewAudio.load();
      if (!preserveElement) {
        this._notifyPreviewAudio = null;
      }
    }
    this._notifyPreviewLoadingKey = "";
    if (this._notifyPreviewAudioObjectUrl) {
      URL.revokeObjectURL(this._notifyPreviewAudioObjectUrl);
      this._notifyPreviewAudioObjectUrl = "";
    }
    if (this._notifyPreviewPlayingKey) {
      this._notifyPreviewPlayingKey = "";
    }
    this._notifyPreviewDuration = 0;
  }

  async _toggleNotifyPreviewAudio(index, fieldKey, value) {
    if (Number.isNaN(index) || !fieldKey || !value) {
      return;
    }

    const previewKey = this._getNotifyPreviewKey(index, fieldKey, value);
    if (this._notifyPreviewPlayingKey === previewKey && this._notifyPreviewAudio) {
      this._stopNotifyPreviewAudio({ preserveElement: true });
      this._rerenderPreservingInputState();
      return;
    }

    this._stopNotifyPreviewAudio();
    this._notifyPreviewLoadingKey = previewKey;
    this._rerenderPreservingInputState();

    const loadToken = this._notifyPreviewAudioLoadToken;
    let objectUrl = "";
    try {
      objectUrl = await this._fetchPickerAudioObjectUrl(this._buildChimePreviewUrl(fieldKey, value));
    } catch (_error) {
      if (loadToken === this._notifyPreviewAudioLoadToken) {
        this._notifyPreviewLoadingKey = "";
        this._data = {
          ...(this._data || {}),
          message: this._t("error.play_chime_preview"),
          message_type: "error",
        };
        this._rerenderPreservingInputState();
      }
      return;
    }

    if (loadToken !== this._notifyPreviewAudioLoadToken) {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
      return;
    }

    const audio = new Audio(objectUrl);
    audio.addEventListener("loadedmetadata", () => {
      if (this._notifyPreviewAudio === audio) {
        this._notifyPreviewDuration = audio.duration;
        this._rerenderPreservingInputState();
      }
    });
    audio.addEventListener("ended", () => {
      if (this._notifyPreviewAudio === audio) {
        this._stopNotifyPreviewAudio();
        this._rerenderPreservingInputState();
      }
    });
    audio.addEventListener("pause", () => {
      if (this._notifyPreviewAudio === audio && audio.ended) {
        return;
      }
      if (this._notifyPreviewAudio === audio && this._notifyPreviewPlayingKey) {
        this._notifyPreviewPlayingKey = "";
        this._rerenderPreservingInputState();
      }
    });
    audio.addEventListener("play", () => {
      if (this._notifyPreviewAudio === audio) {
        this._notifyPreviewLoadingKey = "";
        this._notifyPreviewPlayingKey = previewKey;
        this._notifyPreviewDuration = audio.duration;
        this._rerenderPreservingInputState();
      }
    });
    this._notifyPreviewAudio = audio;
    this._notifyPreviewAudioObjectUrl = objectUrl;
    this._notifyPreviewLoadingKey = "";
    this._notifyPreviewPlayingKey = previewKey;
    const playAttempt = audio.play();
    if (playAttempt && typeof playAttempt.catch === "function") {
      playAttempt.then(() => {
        if (this._notifyPreviewAudio === audio && !audio.paused && !audio.ended) {
          this._notifyPreviewLoadingKey = "";
          this._notifyPreviewPlayingKey = previewKey;
          this._rerenderPreservingInputState();
        }
      });
      playAttempt.catch(() => {
        if (this._notifyPreviewAudio === audio) {
          this._stopNotifyPreviewAudio();
          this._data = {
            ...(this._data || {}),
            message: this._t("error.play_chime_preview"),
            message_type: "error",
          };
          this._rerenderPreservingInputState();
        }
      });
    }
    this._rerenderPreservingInputState();
  }

  async _togglePickerAudio(path, url) {
    if (!path || !url) {
      return;
    }

    if (this._pickerPlayingPath === path && this._pickerAudio) {
      this._stopPickerAudio({ preserveElement: true });
      this._renderPreservingPickerScroll();
      return;
    }

    this._stopPickerAudio();
    this._pickerAudioLoadingPath = path;
    this._pickerError = null;
    this._renderPreservingPickerScroll();

    const loadToken = this._pickerAudioLoadToken;
    let objectUrl = "";
    try {
      objectUrl = await this._fetchPickerAudioObjectUrl(url);
    } catch (_error) {
      if (loadToken === this._pickerAudioLoadToken) {
        this._pickerAudioLoadingPath = "";
        this._pickerError = this._t("error.play_audio_preview");
        this._renderPreservingPickerScroll();
      }
      return;
    }

    if (loadToken !== this._pickerAudioLoadToken) {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
      return;
    }

    const audio = new Audio(objectUrl);
    audio.addEventListener("loadedmetadata", () => {
      if (this._pickerAudio === audio) {
        this._pickerPreviewDuration = audio.duration;
        this._renderPreservingPickerScroll();
      }
    });
    audio.addEventListener("ended", () => {
      if (this._pickerAudio === audio) {
        this._stopPickerAudio();
        this._renderPreservingPickerScroll();
      }
    });
    audio.addEventListener("pause", () => {
      if (this._pickerAudio === audio && audio.ended) {
        return;
      }
      if (this._pickerAudio === audio && this._pickerPlayingPath) {
        this._pickerPlayingPath = "";
        this._renderPreservingPickerScroll();
      }
    });
    audio.addEventListener("play", () => {
      if (this._pickerAudio === audio) {
        this._pickerAudioLoadingPath = "";
        this._pickerPlayingPath = path;
        this._pickerPreviewDuration = audio.duration;
        this._renderPreservingPickerScroll();
      }
    });
    this._pickerAudio = audio;
    this._pickerAudioObjectUrl = objectUrl;
    this._pickerPlayingPath = path;
    const playAttempt = audio.play();
    if (playAttempt && typeof playAttempt.catch === "function") {
      playAttempt.catch(() => {
        if (this._pickerAudio === audio) {
          this._stopPickerAudio();
          this._pickerError = this._t("error.play_audio_preview");
          this._renderPreservingPickerScroll();
        }
      });
    }
    this._renderPreservingPickerScroll();
  }

  async _fetchPickerAudioObjectUrl(url) {
    const response = await this._fetchPickerWithAuth(url);
    if (!response.ok) {
      throw new Error(`Audio preview request failed with status ${response.status}`);
    }

    const audioBlob = await response.blob();
    return URL.createObjectURL(audioBlob);
  }

  _fetchPickerWithAuth(url, init = {}) {
    // Home Assistant owns token refresh and the Authorization header. Using its
    // authenticated fetch helper also works when the auth object does not expose
    // token data to custom panels.
    if (typeof this._hass?.fetchWithAuth === "function") {
      return this._hass.fetchWithAuth(url, init);
    }

    return fetch(url, {
      ...init,
      credentials: "same-origin",
    });
  }

  async _runPickerBrowserCommand(command) {
    if (!this._picker?.field_key) {
      return false;
    }
    this._pickerBusy = true;
    this._pickerError = null;
    this._renderPreservingPickerScroll();
    try {
      const pickerData = await this._hass.callWS(command);
      this._picker = {
        ...(this._picker || {}),
        ...pickerData,
      };
      this._pickerAction = null;
      this._pickerSelectedPath = this._isPickerPathSelectable(this._pickerSelectedPath)
        ? this._pickerSelectedPath
        : this._picker.current_path || "";
      return true;
    } catch (error) {
      const message = error?.message || this._t("error.browser_action");
      if (this._pickerAction) {
        this._pickerAction = {
          ...this._pickerAction,
          error: message,
        };
      } else {
        this._pickerError = message;
      }
      return false;
    } finally {
      this._pickerBusy = false;
      this._renderPreservingPickerScroll();
    }
  }

  async _createPickerFolder() {
    if (!this._picker?.field_key || this._pickerBusy) {
      return;
    }
    this._pickerAction = {
      mode: "create",
      title: this._t("action.create_folder"),
      copy: `Add a new folder inside ${this._picker.current_path || "/"}.`,
      value: "",
      placeholder: this._t("placeholder.new_folder_name"),
      error: "",
    };
    this._render();
  }

  async _renamePickerEntry(path, currentName) {
    if (!this._picker?.field_key || !path || this._pickerBusy) {
      return;
    }
    this._pickerAction = {
      mode: "rename",
      title: this._t("title.rename_item"),
      copy: this._t("notice.rename_item", { name: currentName ? `"${currentName}"` : this._t("label.this_item") }),
      path,
      value: currentName || "",
      placeholder: currentName || this._t("label.new_name"),
      error: "",
    };
    this._render();
  }

  async _deletePickerEntry(path, name) {
    if (!this._picker?.field_key || !path || this._pickerBusy) {
      return;
    }
    this._pickerAction = {
      mode: "delete",
      title: this._t("title.delete_item"),
      copy: this._t("notice.delete_item", { name: name || path }),
      path,
      value: "",
      error: "",
    };
    this._render();
  }

  async _handlePickerUploadSelection(event, { directory }) {
    const input = event.currentTarget;
    this._pickerNativeFileDialogOpen = false;
    const files = Array.from(input?.files || []).filter((file) => this._isPickerAudioFile(file));
    if (!this._picker?.field_key || files.length === 0 || this._pickerBusy) {
      if (input) {
        input.value = "";
      }
      this._render();
      return;
    }

    if (input) {
      input.value = "";
    }

    if (directory) {
      const sourceFolderName = this._getPickerUploadSourceFolderName(files);
      const destinationFolderName = this._getPickerFolderLabel(this._picker.current_path || "/");
      this._pickerAction = {
        mode: "upload",
        title: this._t("action.upload_folder"),
        copy: this._t("notice.upload_folder", { count: files.length, source: sourceFolderName, destination: destinationFolderName }),
        files,
        directory: true,
        error: "",
      };
      this._render();
      return;
    }

    await this._performPickerUpload(files, { directory: false });
  }

  _isPickerAudioFile(file) {
    const filename = String(file?.name || "");
    const extensionIndex = filename.lastIndexOf(".");
    return extensionIndex > 0 && AUDIO_FILE_EXTENSIONS.has(filename.slice(extensionIndex).toLowerCase());
  }

  _openNativePickerFileDialog({ directory }) {
    if (!this._picker?.field_key || this._pickerBusy || this._pickerNativeFileDialogOpen) {
      return;
    }
    this._pickerMenuOpen = false;
    this._pickerNativeFileDialogOpen = true;
    this._render();

    const selector = directory
      ? "[data-picker-folder-input]"
      : "[data-picker-file-input]";
    const input = this.shadowRoot.querySelector(selector);
    if (!input) {
      this._closeNativePickerFileDialog();
      return;
    }

    window.addEventListener("focus", () => {
      window.setTimeout(() => this._closeNativePickerFileDialog(), 0);
    }, { once: true });
    input.click();
  }

  _closeNativePickerFileDialog() {
    if (!this._pickerNativeFileDialogOpen) {
      return;
    }
    this._pickerNativeFileDialogOpen = false;
    this._render();
  }

  _getPickerUploadSourceFolderName(files) {
    const firstRelativePath = files?.[0]?.webkitRelativePath || "";
    const firstSegment = String(firstRelativePath).replace(/\\/g, "/").split("/").filter(Boolean)[0];
    return firstSegment || this._t("label.selected_folder");
  }

  _getPickerFolderLabel(path) {
    const normalized = String(path || "").replace(/\/+$/, "");
    if (!normalized || normalized === "/") {
      return "/";
    }
    const parts = normalized.split("/").filter(Boolean);
    return parts[parts.length - 1] || normalized;
  }

  _getPickerUploadRelativeName(file, { directory }) {
    const normalizedRelativePath = String(file?.webkitRelativePath || "").replace(/\\/g, "/");
    if (directory && normalizedRelativePath) {
      // Preserve the selected folder as the first path segment so its files
      // are uploaded into that folder inside the current destination.
      return normalizedRelativePath.split("/").filter(Boolean).join("/");
    }
    return file?.name || "";
  }

  async _performPickerUpload(files, { directory, overwriteMode = "prompt" } = {}) {
    if (!this._picker?.field_key || !Array.isArray(files) || files.length === 0) {
      return;
    }

    this._pickerBusy = true;
    this._pickerError = null;
    this._renderPreservingPickerScroll();
    try {
      const formData = new FormData();
      formData.append("field_key", this._picker.field_key);
      formData.append("destination_path", this._picker.current_path || "/");
      formData.append("overwrite_mode", overwriteMode);
      for (const file of files) {
        const relativeName = this._getPickerUploadRelativeName(file, { directory });
        formData.append("files", file, relativeName);
      }
      const response = await this._fetchPickerWithAuth("/api/chime_tts/browser/upload", {
        method: "POST",
        body: formData,
      });
      if (response.status === 409) {
        const conflictPayload = await response.json().catch(() => null);
        if (conflictPayload?.error === "upload_conflicts") {
          const conflictCount = Number(conflictPayload.conflict_count || 0);
          const nonExistingCount = Math.max(0, files.length - conflictCount);
          const destinationFolderName = this._getPickerFolderLabel(this._picker.current_path || "/");
          const conflictCopy = this._t(
            nonExistingCount === 0 ? "notice.upload_conflicts_all" : "notice.upload_conflicts",
            { count: conflictCount, destination: destinationFolderName },
          );
          this._pickerAction = {
            mode: "upload_conflicts",
            title: this._t("title.overwrite_files"),
            copy: conflictCopy,
            files,
            directory,
            conflicts: conflictPayload.conflicts || [],
            nonExistingCount,
            error: "",
          };
          return;
        }
      }
      if (!response.ok) {
        throw new Error(await response.text() || this._t("error.upload_files"));
      }
      const pickerData = await response.json();
      this._picker = {
        ...(this._picker || {}),
        ...pickerData,
      };
      this._pickerAction = null;
      this._pickerSelectedPath = this._isPickerPathSelectable(this._pickerSelectedPath)
        ? this._pickerSelectedPath
        : this._picker.current_path || "";
    } catch (error) {
      if (this._pickerAction?.mode === "upload") {
        this._pickerAction = {
          ...this._pickerAction,
          error: error?.message || this._t("error.upload_files"),
        };
      } else {
        this._pickerError = error?.message || this._t("error.upload_files");
      }
    } finally {
      this._pickerBusy = false;
      this._renderPreservingPickerScroll();
    }
  }

  _selectPickerPath(path, kind = "directory") {
    if (!path || kind !== "directory") {
      return;
    }
    this._pickerSelectedPath = path;
    this._render();
  }

  _isPickerPathSelectable(path) {
    if (!path || !this._picker) {
      return false;
    }
    if (path === this._picker.current_path) {
      return Boolean(this._picker.current_path_allowed);
    }
    return Boolean((this._picker.items || []).some(
      (item) => item?.is_dir && item?.path === path,
    ));
  }

  _closePickerAction() {
    this._pickerAction = null;
    this._render();
  }

  _runPickerActionSecondary() {
    if (this._pickerAction?.mode === "upload_conflicts" && this._pickerAction.nonExistingCount > 0) {
      this._performPickerUpload(this._pickerAction.files || [], {
        directory: Boolean(this._pickerAction.directory),
        overwriteMode: "skip",
      });
    }
  }

  async _submitPickerAction() {
    if (!this._pickerAction || this._pickerBusy || !this._picker?.field_key) {
      return;
    }

    const value = String(this._pickerAction.value || "").trim();
    let command = null;

    if (this._pickerAction.mode === "create") {
      if (!value) {
        this._pickerAction = { ...this._pickerAction, error: this._t("error.folder_name_required") };
        this._render();
        return;
      }
      command = {
        type: "chime_tts/browser_create_folder",
        field_key: this._picker.field_key,
        path: this._picker.current_path || "/",
        name: value,
      };
    } else if (this._pickerAction.mode === "rename") {
      if (!value) {
        this._pickerAction = { ...this._pickerAction, error: this._t("error.new_name_required") };
        this._render();
        return;
      }
      command = {
        type: "chime_tts/browser_rename_entry",
        field_key: this._picker.field_key,
        path: this._pickerAction.path,
        new_name: value,
      };
    } else if (this._pickerAction.mode === "delete") {
      if (
        this._pickerPlayingPath === this._pickerAction.path
        || this._pickerAudioLoadingPath === this._pickerAction.path
      ) {
        this._stopPickerAudio();
      }
      command = {
        type: "chime_tts/browser_delete_entry",
        field_key: this._picker.field_key,
        path: this._pickerAction.path,
      };
    } else if (this._pickerAction.mode === "upload") {
      await this._performPickerUpload(this._pickerAction.files || [], {
        directory: Boolean(this._pickerAction.directory),
      });
      return;
    } else if (this._pickerAction.mode === "upload_conflicts") {
      await this._performPickerUpload(this._pickerAction.files || [], {
        directory: Boolean(this._pickerAction.directory),
        overwriteMode: "overwrite",
      });
      return;
    }

    if (!command) {
      return;
    }

    await this._runPickerBrowserCommand(command);
  }

  async _choosePickerPath(path) {
    const fieldKey = this._picker?.field_key;
    if (!fieldKey || !path) {
      return;
    }

    const currentPath = this._picker?.current_path || "";
    let validation = {
      field_key: fieldKey,
      path,
      valid: Boolean(this._picker?.current_path_allowed && path === currentPath),
      exists: true,
      tone: this._picker?.current_path_allowed && path === currentPath ? "success" : "error",
      message: this._picker?.current_path_validation_message || "",
      badges: this._picker?.current_path_badges || [],
    };
    if (path !== currentPath) {
      try {
        validation = await this._hass.callWS({
          type: "chime_tts/validate_path",
          field_key: fieldKey,
          path,
        });
      } catch (error) {
        validation = {
          field_key: fieldKey,
          path,
          valid: false,
          exists: false,
          tone: "error",
          message: error?.message || this._t("error.validate_folder"),
          badges: [],
        };
      }
    }

    if (!validation.valid) {
      this._pickerError = validation.message || this._t("error.folder_not_selectable");
      this._render();
      return;
    }

    this._draftValues = {
      ...(this._draftValues || {}),
      [fieldKey]: path,
    };
    if (this._invalidPathOverrides?.[fieldKey]) {
      const nextOverrides = { ...(this._invalidPathOverrides || {}) };
      delete nextOverrides[fieldKey];
      this._invalidPathOverrides = nextOverrides;
    }
    this._pathValidationState = {
      ...(this._pathValidationState || {}),
      [fieldKey]: validation,
    };
    if (this._clientErrors[fieldKey]) {
      const nextErrors = { ...(this._clientErrors || {}) };
      delete nextErrors[fieldKey];
      this._clientErrors = nextErrors;
    }
    this._isDirty = this._hasValueChanges();
    this._closePicker();
  }

  _findFieldLabel(fieldKey) {
    const sections = this._data?.sections || [];
    for (const section of sections) {
      for (const field of section.fields || []) {
        if (field.key === fieldKey) {
          return field.label;
        }
      }
    }
    return this._t("action.select_folder");
  }

  _findField(fieldKey) {
    const sections = this._data?.sections || [];
    for (const section of sections) {
      for (const field of section.fields || []) {
        if (field.key === fieldKey) {
          return field;
        }
      }
    }
    return null;
  }

  _findNotifyProfileField(fieldKey) {
    const section = (this._data?.sections || []).find((item) => item.key === "notify_profiles");
    return (section?.profile_fields || []).find((field) => field.key === fieldKey) || null;
  }

  _isPathFieldKey(fieldKey) {
    const sections = this._data?.sections || [];
    for (const section of sections) {
      for (const field of section.fields || []) {
        if (field.key === fieldKey) {
          return Boolean(field.can_browse);
        }
      }
    }
    return false;
  }

  _hasInvalidPathChanges() {
    const sections = this._data?.sections || [];
    for (const section of sections) {
      for (const field of section.fields || []) {
        if (this._hasBlockingPathValidationError(field)) {
          return true;
        }
      }
    }
    return false;
  }

  _hasBlockingPathValidationError(field, value = this._draftValues?.[field?.key]) {
    if (
      !field?.can_browse
      || !this._isFieldChanged(field.key)
      || this._invalidPathOverrides?.[field.key]
      || String(value ?? "").trim() === ""
    ) {
      return false;
    }
    return this._getPathValidationState(field)?.valid === false;
  }

  _scrollToFirstValidationError() {
    window.requestAnimationFrame(() => {
      const error = this.shadowRoot?.querySelector(
        ".notify-profile-validation-error, .field.error",
      );
      if (!error) {
        return;
      }
      const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
      error.scrollIntoView({
        behavior: reduceMotion ? "auto" : "smooth",
        block: "center",
      });
      if (reduceMotion) {
        return;
      }
      error.classList.remove("validation-flash");
      void error.offsetWidth;
      error.classList.add("validation-flash");
      error.addEventListener("animationend", () => {
        error.classList.remove("validation-flash");
      }, { once: true });
    });
  }

  _hasValueChanges() {
    if (this._hasNotifyProfileChanges()) {
      return true;
    }
    const savedValues = this._data?.values || {};
    const draftValues = this._draftValues || {};
    const keys = new Set([...Object.keys(savedValues), ...Object.keys(draftValues)]);

    for (const key of keys) {
      if (this._normalizeForCompare(savedValues[key], key) !== this._normalizeForCompare(draftValues[key], key)) {
        return true;
      }
    }

    return false;
  }

  _normalizeForCompare(value, fieldKey = null) {
    if (value === null || value === undefined) {
      return "";
    }
    if (typeof value === "boolean") {
      return value ? "true" : "false";
    }
    if (Array.isArray(value) || (typeof value === "object" && value !== null)) {
      return JSON.stringify(value);
    }
    const normalized = String(value);
    if (fieldKey && this._isPathFieldKey(fieldKey)) {
      return this._normalizePathForCompare(normalized);
    }
    return normalized;
  }

  _normalizePathForCompare(value) {
    const normalized = String(value || "");
    if (normalized === "/") {
      return "/";
    }
    return normalized.replace(/\/+$/, "");
  }

  _validateRequiredFields() {
    const errors = {};
    const sections = this._data?.sections || [];
    for (const section of sections) {
      for (const field of section.fields || []) {
        if (!field.required) {
          continue;
        }
        const value = this._draftValues?.[field.key];
        if (field.type === "boolean") {
          continue;
        }
        if (value === null || value === undefined || String(value).trim() === "") {
          errors[field.key] = "required";
        }
      }
    }

    const randomChimeSets = this._randomChimeSetsDraft();
    if (randomChimeSets.some((chimeSet) => (
      !String(chimeSet?.name || "").trim()
      || !Array.isArray(chimeSet?.chimes)
      || chimeSet.chimes.length === 0
    ))) {
      errors.chime_sets = "invalid_chime_sets";
      this._expandedChapters = { ...(this._expandedChapters || {}), chime_sets: true };
    }

    const notifyProfileErrors = this._cloneNotifyProfileErrors(this._notifyProfileClientErrors || []);
    for (let index = 0; index < (this._draftNotifyProfiles || []).length; index += 1) {
      const profile = this._draftNotifyProfiles[index] || {};
      if (!String(profile.name ?? "").trim()) {
        notifyProfileErrors[index] = { ...(notifyProfileErrors[index] || {}), name: "required" };
      }
      if (this._notifyTargets(profile).length === 0) {
        notifyProfileErrors[index] = { ...(notifyProfileErrors[index] || {}), targets: "required" };
      }
      if (Object.keys(notifyProfileErrors[index] || {}).length > 0) {
        this._expandedNotifyProfiles = {
          ...(this._expandedNotifyProfiles || {}),
          [index]: true,
        };
      }
    }
    this._notifyProfileClientErrors = notifyProfileErrors;
    return errors;
  }

  _buildEmptyNotifyProfile() {
    return {
      name: "",
      entity_id: "",
      targets: [],
      chime_path: "",
      end_chime_path: "",
      tts_platform: "",
      language: "",
      voice: "",
      tld: "",
      offset: "",
      crossfade: "",
      final_delay: "",
      tts_speed: "",
      tts_pitch: "",
      volume_level: "",
      audio_conversion: "",
      options: "",
      pre_script: "",
      post_script: "",
      announce: false,
      cache: false,
      fade_audio: false,
      join_players: false,
      unjoin_players: false,
    };
  }

  _cloneNotifyProfiles(profiles) {
    return (profiles || []).map((profile) => ({ ...this._buildEmptyNotifyProfile(), ...(profile || {}) }));
  }

  _cloneNotifyProfileErrors(errors) {
    return (errors || []).map((profileErrors) => ({ ...(profileErrors || {}) }));
  }

  _getNotifyProfileErrors(index) {
    return {
      ...((this._data?.notify_profile_errors || [])[index] || {}),
      ...((this._notifyProfileClientErrors || [])[index] || {}),
    };
  }

  _getNotifyProfileTestState(index) {
    const state = {
      open: false,
      message: "",
      sending: false,
      sentAt: 0,
      ...((this._notifyProfileTests || {})[index] || {}),
    };
    return {
      ...state,
      sent: Boolean(state.sentAt && Date.now() - state.sentAt < 2000),
    };
  }

  _openNotifyProfileTest(index) {
    if (Number.isNaN(index)) {
      return;
    }
    this._clearNotifyProfileTestTimer(index);
    this._notifyProfileTests = {
      ...(this._notifyProfileTests || {}),
      [index]: {
        open: true,
        message: "",
        sending: false,
        sentAt: 0,
      },
    };
    this._render();
  }

  _closeNotifyProfileTest(index) {
    if (Number.isNaN(index)) {
      return;
    }
    this._clearNotifyProfileTestTimer(index);
    const nextState = { ...(this._notifyProfileTests || {}) };
    delete nextState[index];
    this._notifyProfileTests = nextState;
    this._render();
  }

  _updateNotifyProfileTestMessage(index, message) {
    if (Number.isNaN(index)) {
      return;
    }
    this._clearNotifyProfileTestTimer(index);
    const current = this._getNotifyProfileTestState(index);
    this._notifyProfileTests = {
      ...(this._notifyProfileTests || {}),
      [index]: {
        ...current,
        open: true,
        message,
        sentAt: 0,
      },
    };
  }

  _handleNotifyProfileTestMessageInput(event) {
    const field = event.currentTarget;
    const index = Number(field?.dataset?.notifyIndex);
    if (Number.isNaN(index)) {
      return;
    }

    this._updateNotifyProfileTestMessage(index, field.value);

    const row = field.closest(".notify-profile-actions.testing");
    const sendButton = row?.querySelector(`[data-run-notify-inline-test="${this._escapeSelectorValue(String(index))}"]`);
    if (sendButton) {
      const state = this._getNotifyProfileTestState(index);
      sendButton.disabled = state.sending || this._isNotifyProfileDirty(index) || !String(state.message || "").trim();
    }
  }

  async _runNotifyProfileTest(index) {
    if (Number.isNaN(index)) {
      return;
    }
    const profile = (this._draftNotifyProfiles || [])[index];
    const service = String(profile?.name || "").trim();
    const current = this._getNotifyProfileTestState(index);
    const message = String(current.message || "").trim();
    if (!service || !message || current.sending || this._isNotifyProfileDirty(index)) {
      return;
    }

    this._clearNotifyProfileTestTimer(index);
    this._notifyProfileTests = {
      ...(this._notifyProfileTests || {}),
      [index]: {
        ...current,
        sending: true,
        sentAt: 0,
      },
    };
    this._render();

    try {
      await this._hass.callService("notify", service, { message });
      this._notifyProfileTests = {
        ...(this._notifyProfileTests || {}),
        [index]: {
          ...this._getNotifyProfileTestState(index),
          open: true,
          message: current.message,
          sending: false,
          sentAt: Date.now(),
        },
      };
      this._notifyProfileTestTimers = {
        ...(this._notifyProfileTestTimers || {}),
        [index]: window.setTimeout(() => {
          const nextState = this._getNotifyProfileTestState(index);
          this._clearNotifyProfileTestTimer(index);
          this._notifyProfileTests = {
            ...(this._notifyProfileTests || {}),
            [index]: {
              ...nextState,
              open: true,
              sending: false,
              sentAt: 0,
            },
          };
          this._render();
        }, 2000),
      };
    } catch (error) {
      this._data = {
        ...(this._data || {}),
        message: error?.message || this._t("error.send_notification", { service }),
        message_type: "error",
      };
      this._notifyProfileTests = {
        ...(this._notifyProfileTests || {}),
        [index]: {
          ...this._getNotifyProfileTestState(index),
          open: true,
          message: current.message,
          sending: false,
          sentAt: 0,
        },
      };
      this._showSaveResult("error");
    } finally {
      this._render();
    }
  }

  _clearNotifyProfileTestTimer(index) {
    const timer = this._notifyProfileTestTimers?.[index];
    if (!timer) {
      return;
    }
    window.clearTimeout(timer);
    const nextTimers = { ...(this._notifyProfileTestTimers || {}) };
    delete nextTimers[index];
    this._notifyProfileTestTimers = nextTimers;
  }

  _clearAllNotifyProfileTestTimers() {
    for (const key of Object.keys(this._notifyProfileTestTimers || {})) {
      this._clearNotifyProfileTestTimer(Number(key));
    }
  }

  _hasNotifyProfileChanges() {
    const savedProfiles = this._data?.notify_profiles || [];
    const draftProfiles = this._draftNotifyProfiles || [];
    if (savedProfiles.length !== draftProfiles.length) {
      return true;
    }
    return draftProfiles.some((_, index) => this._isNotifyProfileDirty(index));
  }

  _renderTransientMessage(data, sectionCount = 0) {
    const isTransientError = Boolean(
      data?.message
      && data?.message_type === "error"
      && sectionCount > 0,
    );
    this._transientBannerRegion.innerHTML = isTransientError
      ? `<div class="transient-banner" role="alert">${this._escapeHtml(data.message)}</div>`
      : "";

    if (isTransientError) {
      this._scheduleMessageClear();
    }
  }

  _scheduleMessageClear() {
    const message = this._data?.message;
    const messageType = this._data?.message_type;
    if (!message) {
      return;
    }

    const messageKey = `${messageType || ""}:${message}`;
    if (this._messageTimeout && this._scheduledMessageKey === messageKey) {
      return;
    }
    if (this._messageTimeout) {
      window.clearTimeout(this._messageTimeout);
    }
    this._scheduledMessageKey = messageKey;
    this._messageTimeout = window.setTimeout(() => {
      const currentMessageKey = `${this._data?.message_type || ""}:${this._data?.message || ""}`;
      if (currentMessageKey !== messageKey) {
        return;
      }
      this._data = {
        ...this._data,
        message: null,
        message_type: null,
      };
      this._messageTimeout = null;
      this._scheduledMessageKey = "";
      this._render();
    }, 5000);
  }

  _clearSaveResult() {
    this._saveResult = null;
    if (this._saveResultTimeout) {
      window.clearTimeout(this._saveResultTimeout);
      this._saveResultTimeout = null;
    }
  }

  _showSaveResult(result) {
    this._clearSaveResult();
    this._saveResult = result;
    this._saveResultTimeout = window.setTimeout(() => {
      this._saveResult = null;
      this._saveResultTimeout = null;
      this._renderTopbar(this._data || {});
    }, 1500);
  }

  _closePanel() {
    const fallbackPath = "/config/dashboard";
    const sameOriginReferrer = document.referrer
      && (() => {
        try {
          return new URL(document.referrer).origin === window.location.origin;
        } catch (_error) {
          return false;
        }
      })();

    if (
      sameOriginReferrer
      && window.history.length > 1
      && !String(window.location.pathname || "").startsWith(fallbackPath)
    ) {
      window.history.back();
      window.setTimeout(() => {
        if (String(window.location.pathname || "").includes("/chime-tts")) {
          window.location.assign(fallbackPath);
        }
      }, 250);
      return;
    }

    window.location.assign(fallbackPath);
  }

  _toggleHassMenu() {
    this.dispatchEvent(
      new Event("hass-toggle-menu", {
        bubbles: true,
        composed: true,
      }),
    );
  }

  _formatError(errorKey) {
    const randomSetErrors = {
      invalid_chime_sets: "Each Chime Set needs a name and at least one chime.",
      duplicate_chime_set_name: "Chime Set names must be unique.",
      invalid_chime_member: "Sets may contain only available bundled or custom chimes.",
    };
    if (randomSetErrors[errorKey]) return randomSetErrors[errorKey];
    const translated = this._t(`validation.${errorKey}`);
    return translated === `validation.${errorKey}` ? errorKey : translated;
  }

  _escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  _escapeAttribute(value) {
    return this._escapeHtml(value);
  }
}

if (!customElements.get(PANEL_TAG)) {
  customElements.define(PANEL_TAG, ChimeTtsSettingsPanel);
}
