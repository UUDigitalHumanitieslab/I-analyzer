import {
    IconDefinition as RegularIconDefinition,
    faNewspaper,
} from '@fortawesome/free-regular-svg-icons';
import {
    IconDefinition as SolidIconDefinition,
    faAngleDown, faAngleUp, faArrowLeft, faArrowRight, faAt, faBook, faBookmark, faBookOpen, faBuilding, faChartColumn,
    faCheck, faChevronLeft, faChevronRight, faCog, faCogs, faDatabase, faDiagramProject,
    faDownload, faEnvelope, faEye, faFilter, faHistory, faImage, faInfo, faInfoCircle, faLink, faList, faLocationDot, faLock,
    faMinus, faPalette, faPencil, faPlus, faQuestionCircle, faSearch, faSearchMinus, faSearchPlus, faSignOut,
    faSortAlphaAsc, faSortAlphaDesc, faSortNumericAsc, faSortNumericDesc, faSquare,
    faTable, faTags, faTimes, faTrashCan, faUndo, faUpload, faUser
} from '@fortawesome/free-solid-svg-icons';

type IconDefinition = SolidIconDefinition | RegularIconDefinition;
export interface Icons {
    [alias: string]: IconDefinition;
}

export const userIcons: Icons = {
    user: faUser,
    email: faAt,
    password: faLock,
    logout: faSignOut,
};

export const navIcons: Icons = {
    corpora: faDatabase,
    searchHistory: faHistory,
    manual: faBook,
    about: faInfoCircle,
    settings: faCog,
    admin: faCogs,
    downloads: faDownload,
    tags: faTags,
};

export const actionIcons: Icons = {
    search: faSearch,
    help: faInfoCircle,
    helpAlt: faQuestionCircle,
    download: faDownload,
    upload: faUpload,
    config: faCog,
    email: faEnvelope,
    more: faPlus,
    less: faMinus,
    prev: faArrowLeft,
    next: faArrowRight,
    link: faLink,
    dropdown: faAngleDown,
    dropup: faAngleUp,
    add: faPlus,
    remove: faTimes,
    delete: faTrashCan,
    edit: faPencil,
    view: faEye,
};

export const formIcons: Icons = {
    confirm: faCheck,
    reset: faTimes,
};

export const corpusIcons: Icons = {
    search: actionIcons.search,
    wordModels: faDiagramProject,
    info: faInfo,
    infoAlt: faInfoCircle,
};

export const searchIcons: Icons = {
    search: actionIcons.search,
    filter: faFilter,
    documents: faList,
    visualizations: faChartColumn,
};

export const filterIcons: Icons = {
    toggle: searchIcons.filter,
    clear: actionIcons.delete,
};

export const sortIcons: Icons = {
    alphaDesc: faSortAlphaDesc,
    alphaAsc: faSortAlphaAsc,
    numericDesc: faSortNumericDesc,
    numericAsc: faSortNumericAsc,
};

export const visualizationIcons: Icons = {
    chart: faChartColumn,
    table: faTable,
    palette: faPalette,
    swatch: faSquare,
};

export const scanIcons: Icons = {
    zoomIn: faSearchPlus,
    zoomOut: faSearchMinus,
    zoomReset: faUndo,
    prev: faChevronLeft,
    next: faChevronRight,
};

export const documentIcons: Icons = {
    text: faBook,
    scan: faImage,
    scanAlt: faNewspaper,
    context: faBookOpen,
};

export const entityIcons: Icons = {
    person: faUser,
    location: faLocationDot,
    organization: faBuilding,
    miscellaneous: faBookmark,
}
